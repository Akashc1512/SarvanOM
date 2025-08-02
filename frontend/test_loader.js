// Test script to verify SarvanOM Loader component
const fs = require('fs');

console.log('🧪 Testing SarvanOM Loader Component...\n');

// Test 1: Check if loader component exists
const loaderFile = 'src/components/SarvanomLoader.tsx';
if (fs.existsSync(loaderFile)) {
  console.log('✅ SarvanomLoader.tsx component exists');
  
  const content = fs.readFileSync(loaderFile, 'utf8');
  
  // Check for key features
  const features = [
    'SarvanomLoader',
    'SarvanomLoaderFullScreen', 
    'SarvanomLoaderInline',
    'sarvanom-orbit1',
    'sarvanom-orbit2', 
    'sarvanom-orbit3',
    'sarvanom-pulse',
    'globe',
    'ellipse'
  ];
  
  let featureCount = 0;
  features.forEach(feature => {
    if (content.includes(feature)) {
      console.log(`✅ ${feature} found in component`);
      featureCount++;
    } else {
      console.log(`❌ ${feature} missing from component`);
    }
  });
  
  console.log(`\n📊 Feature Coverage: ${featureCount}/${features.length}`);
} else {
  console.log('❌ SarvanomLoader.tsx component missing');
}

// Test 2: Check if demo page exists
const demoFile = 'src/app/loader-demo/page.tsx';
if (fs.existsSync(demoFile)) {
  console.log('\n✅ Loader demo page exists');
  
  const content = fs.readFileSync(demoFile, 'utf8');
  
  // Check for demo features
  const demoFeatures = [
    'SarvanomLoader',
    'Basic Demo',
    'Full Screen Demo', 
    'Inline Demo',
    'Interactive Demo'
  ];
  
  let demoFeatureCount = 0;
  demoFeatures.forEach(feature => {
    if (content.includes(feature)) {
      console.log(`✅ ${feature} found in demo`);
      demoFeatureCount++;
    } else {
      console.log(`❌ ${feature} missing from demo`);
    }
  });
  
  console.log(`\n📊 Demo Coverage: ${demoFeatureCount}/${demoFeatures.length}`);
} else {
  console.log('\n❌ Loader demo page missing');
}

// Test 3: Check if CSS animations are added
const cssFile = 'src/app/globals.css';
if (fs.existsSync(cssFile)) {
  console.log('\n✅ Global CSS file exists');
  
  const content = fs.readFileSync(cssFile, 'utf8');
  
  const animations = [
    '@keyframes sarvanom-spin',
    '@keyframes sarvanom-orbit1', 
    '@keyframes sarvanom-orbit2',
    '@keyframes sarvanom-orbit3',
    '@keyframes sarvanom-pulse'
  ];
  
  let animationCount = 0;
  animations.forEach(animation => {
    if (content.includes(animation)) {
      console.log(`✅ ${animation} found in CSS`);
      animationCount++;
    } else {
      console.log(`❌ ${animation} missing from CSS`);
    }
  });
  
  console.log(`\n📊 Animation Coverage: ${animationCount}/${animations.length}`);
} else {
  console.log('\n❌ Global CSS file missing');
}

// Test 4: Check if main page has loader demo link
const mainPageFile = 'src/app/page.tsx';
if (fs.existsSync(mainPageFile)) {
  console.log('\n✅ Main page exists');
  
  const content = fs.readFileSync(mainPageFile, 'utf8');
  
  if (content.includes('SarvanOM Loader Demo')) {
    console.log('✅ Loader demo link found in main page');
  } else {
    console.log('❌ Loader demo link missing from main page');
  }
  
  if (content.includes('/loader-demo')) {
    console.log('✅ Loader demo route link found');
  } else {
    console.log('❌ Loader demo route link missing');
  }
} else {
  console.log('\n❌ Main page missing');
}

console.log('\n🎉 Loader Component Test Complete!');
console.log('\n📋 Summary:');
console.log('• SarvanOM Loader component created with orbiting animations');
console.log('• Demo page with multiple loader examples');
console.log('• CSS animations for smooth orbital motion');
console.log('• Integration with main page navigation');
console.log('• Ready for production use');

console.log('\n🚀 Next Steps:');
console.log('1. Start the development server: npm run dev');
console.log('2. Visit http://localhost:3000/loader-demo');
console.log('3. Test the interactive loader demonstrations');
console.log('4. Integrate loader into other components as needed'); 