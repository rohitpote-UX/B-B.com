import { NextRequest, NextResponse } from 'next/server';
import { getSessionFromRequest } from '@/lib/auth';
import { sql, initSchema } from '@/lib/db';
import { collectFromSource } from '@/lib/collector';

export async function GET(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();
  const jobs = await sql`SELECT * FROM bb_research_jobs ORDER BY created_at DESC LIMIT 50`;
  return NextResponse.json({ jobs });
}

export async function POST(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();

  const body = await req.json().catch(() => ({}));
  const sourceId = body.source_id;

  // Get sources to run
  const sources = sourceId
    ? await sql`SELECT id, name FROM bb_research_sources WHERE id = ${sourceId} AND enabled = true`
    : await sql`SELECT id, name FROM bb_research_sources WHERE enabled = true LIMIT 10`;

  if (!sources.length) {
    return NextResponse.json({ error: 'No enabled sources found.' }, { status: 400 });
  }

  const jobIds: number[] = [];
  const results = [];

  for (const source of sources) {
    // Create job record
    const jobRows = await sql`
      INSERT INTO bb_research_jobs (source_id, source_name, job_type, status, started_at, triggered_by)
      VALUES (${source.id}, ${source.name}, 'rss_collect', 'running', NOW(), 'manual')
      RETURNING id
    `;
    const jobId = jobRows[0].id;
    jobIds.push(jobId);

    try {
      const result = await collectFromSource(Number(source.id));
      await sql`
        UPDATE bb_research_jobs
        SET status = 'completed', completed_at = NOW(),
            items_collected = ${result.itemsCollected},
            items_new = ${result.itemsNew},
            items_duplicate = ${result.itemsDuplicate},
            findings_created = ${result.findingsCreated},
            error_summary = ${JSON.stringify(result.errors)}
        WHERE id = ${jobId}
      `;
      results.push({ jobId, ...result });
    } catch (err) {
      await sql`
        UPDATE bb_research_jobs
        SET status = 'failed', completed_at = NOW(),
            error_summary = ${JSON.stringify([String(err)])}
        WHERE id = ${jobId}
      `;
      results.push({ sourceId: source.id, sourceName: source.name, jobId, success: false, error: String(err) });
    }
  }

  await sql`INSERT INTO bb_audit_logs (action, details) VALUES ('collection_job_run', ${JSON.stringify({ jobIds, sourceCount: sources.length })})`;
  return NextResponse.json({ ok: true, jobs: results });
}
