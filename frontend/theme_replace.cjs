const fs = require('fs');
const path = require('path');

const dir = 'c:\\Users\\Rohit Pote\\Desktop\\Personal Projects\\B&B.com\\frontend\\src';

const map = {
  'bg-[#0a0a0a]': 'bg-theme-bg',
  'bg-[#171717]': 'bg-theme-elevated',
  'bg-[#262626]': 'bg-theme-subtle',
  'bg-[#404040]': 'bg-theme-strong',
  'bg-[#737373]': 'bg-theme-dim',
  'bg-black': 'bg-theme-bg',
  'bg-white': 'bg-theme-text',
  
  'border-[#262626]': 'border-theme-border',
  'border-[#404040]': 'border-theme-strong',
  'border-[#0a0a0a]': 'border-theme-bg',
  'border-white': 'border-theme-text',
  'border-black': 'border-theme-bg',
  
  'text-white': 'text-theme-text',
  'text-[#a3a3a3]': 'text-theme-secondary',
  'text-[#737373]': 'text-theme-muted',
  'text-[#404040]': 'text-theme-dim',
  'text-[#171717]': 'text-theme-elevated',
  'text-black': 'text-theme-bg',
  
  'fill-white': 'fill-theme-text',
  
  'hover:text-white': 'hover:text-theme-text',
  'hover:text-black': 'hover:text-theme-bg',
  'hover:bg-white': 'hover:bg-theme-text',
  'hover:border-white': 'hover:border-theme-text',
  'hover:border-[#404040]': 'hover:border-theme-strong',
  'hover:bg-[#171717]': 'hover:bg-theme-elevated',
  'hover:bg-[#262626]': 'hover:bg-theme-subtle'
};

function processDirectory(directory) {
  const files = fs.readdirSync(directory);
  
  for (const file of files) {
    const fullPath = path.join(directory, file);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory() && !fullPath.includes('node_modules')) {
      processDirectory(fullPath);
    } else if (fullPath.endsWith('.jsx') || fullPath.endsWith('.js')) {
      let content = fs.readFileSync(fullPath, 'utf8');
      
      const sortedKeys = Object.keys(map).sort((a,b) => b.length - a.length);
      
      for (const key of sortedKeys) {
        // We only replace whole words to avoid partial matches
        // But since they are tailwind classes, using regex with boundaries is safe
        // However, hyphen and brackets aren't word boundaries in regex.
        // Doing split-join is safe enough since we sorted by length.
        content = content.split(key).join(map[key]);
      }
      
      fs.writeFileSync(fullPath, content, 'utf8');
    }
  }
}

processDirectory(dir);
console.log('Done mapping themes');
