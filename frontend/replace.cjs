const fs = require('fs');
const path = require('path');

const dir = 'c:\\Users\\Rohit Pote\\Desktop\\Personal Projects\\B&B.com\\frontend\\src';

const map = {
  'text-hero': 'text-[4rem] sm:text-[6rem] lg:text-[8rem] font-[var(--font-display)] font-medium leading-[0.9] tracking-tighter text-white',
  'text-display': 'text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-[var(--font-display)] font-medium leading-[1.05] tracking-tight text-white',
  'text-heading': 'text-[2rem] sm:text-[3rem] lg:text-[3.5rem] font-medium leading-[1.1] tracking-tight text-white',
  'text-body': 'text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight',
  'text-label': 'text-[0.75rem] font-medium uppercase tracking-[0.15em]',
  
  'btn-primary': 'inline-flex items-center justify-center px-10 py-5 bg-transparent border border-white text-white text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:bg-white hover:text-black',
  'btn-ghost': 'inline-flex items-center justify-center px-10 py-5 bg-transparent border border-[#262626] text-white text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:border-white',
  
  'container-fluid': 'w-full max-w-[1536px] mx-auto px-8 md:px-16',
  'section-padding': 'py-[140px] lg:py-[240px]',
  'grid-12': 'grid grid-cols-12 gap-8 lg:gap-16',
  'split-section': 'grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-[160px] items-center',
  'glass-nav': 'bg-[#0a0a0a]/90 backdrop-blur-md',
  
  'product-card': 'group block',
  'image-wrapper mb-10': 'aspect-square bg-[#171717] p-8 lg:p-12 mb-10 flex items-center justify-center overflow-hidden',
  'image-wrapper relative mb-8': 'aspect-square bg-[#171717] p-8 lg:p-12 relative mb-8 flex items-center justify-center overflow-hidden',
  'image-wrapper relative': 'aspect-square bg-[#171717] p-8 lg:p-12 relative flex items-center justify-center overflow-hidden',
  'image-wrapper': 'aspect-square bg-[#171717] p-8 lg:p-12 flex items-center justify-center overflow-hidden',
};

const vars = {
  'var(--color-bg-elevated)': '#171717',
  'var(--color-bg-subtle)': '#262626',
  'var(--color-bg)': '#0a0a0a',
  'var(--color-border)': '#262626',
  'var(--color-text-secondary)': '#a3a3a3',
  'var(--color-text-muted)': '#737373',
  'var(--color-text-dim)': '#404040',
  'var(--color-text)': '#ffffff'
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
        content = content.replaceAll(key, map[key]);
      }
      
      for (const key of Object.keys(vars)) {
        content = content.replaceAll(key, vars[key]);
      }
      
      fs.writeFileSync(fullPath, content, 'utf8');
    }
  }
}

processDirectory(dir);
console.log('Done mapping CSS values');
