import assert from 'node:assert';
import { generateDeepCompareData } from '../src/data/deepCompareData.js';
import { resolveComparisonProfile, detectCategoryProfileType, areCategoriesCompatible } from '../src/lib/comparisonProfiles.ts';

console.log('=== BRANDBATTLE COMPARISON ENGINE VERIFICATION ===\n');

// 1. Exact Screenshot Products
const campusSneakers = {
  id: 1199,
  name: 'Campus Men Sneakers',
  brand: 'Campus',
  category: 'Shoes',
  rating: 5.0,
  totalReviews: 28,
  bestPrice: 1752,
  originalPrice: 2998,
  dealScore: 99,
  specs: { "Price (INR)": "₹1,752", "Rating": "5.0/5", "Reviews": 28 },
  features: ["shoes"],
  prices: [{ platform: "amazon", price: 1752, original: 2998, delivery: 4, rating: 4, currency: "INR" }]
};

const pumaBadminton = {
  id: 1113,
  name: 'Puma Badminton Smash Sprint Shoes',
  brand: 'Puma',
  category: 'Shoes',
  rating: 4.4,
  totalReviews: 8600,
  bestPrice: 1756,
  originalPrice: 4998,
  dealScore: 99,
  specs: { "Price (INR)": "₹1,756", "Rating": "4.4/5", "Reviews": 8600 },
  features: ["shoes"],
  prices: [{ platform: "amazon", price: 1756, original: 4998, delivery: 5, rating: 3.9, currency: "INR" }]
};

console.log('Test 1: Testing Campus Men Sneakers vs Puma Badminton Smash Sprint Shoes...');
const shoeCompare = generateDeepCompareData(campusSneakers, pumaBadminton, 0);

assert.strictEqual(shoeCompare.categoryProfile.id, 'FOOTWEAR', 'Profile must be FOOTWEAR');
assert.strictEqual(shoeCompare.categoryProfile.title, 'REAL-WORLD PERFORMANCE', 'Title must be REAL-WORLD PERFORMANCE');
assert.strictEqual(shoeCompare.categoryProfile.subtitle, 'Footwear comparison signals based on available product attributes and user feedback.');

// Verify NO electronics metrics leaked into shoe comparison
assert.strictEqual(shoeCompare.realWorldPerformance.product1.battery, undefined, 'Shoe product1 must NOT have battery');
assert.strictEqual(shoeCompare.realWorldPerformance.product1.heating, undefined, 'Shoe product1 must NOT have heating');
assert.strictEqual(shoeCompare.realWorldPerformance.product1.gaming, undefined, 'Shoe product1 must NOT have gaming');
assert.strictEqual(shoeCompare.realWorldPerformance.product1.camera, undefined, 'Shoe product1 must NOT have camera');

assert.strictEqual(shoeCompare.realWorldPerformance.product2.battery, undefined, 'Shoe product2 must NOT have battery');
assert.strictEqual(shoeCompare.realWorldPerformance.product2.heating, undefined, 'Shoe product2 must NOT have heating');
assert.strictEqual(shoeCompare.realWorldPerformance.product2.gaming, undefined, 'Shoe product2 must NOT have gaming');
assert.strictEqual(shoeCompare.realWorldPerformance.product2.camera, undefined, 'Shoe product2 must NOT have camera');

// Verify Footwear metrics are present
assert.ok(shoeCompare.realWorldPerformance.product1.comfort > 0, 'Must have comfort metric');
assert.ok(shoeCompare.realWorldPerformance.product1.cushioning > 0, 'Must have cushioning metric');
assert.ok(shoeCompare.realWorldPerformance.product1.grip > 0, 'Must have grip metric');
assert.ok(shoeCompare.realWorldPerformance.product1.stability > 0, 'Must have stability metric');
assert.ok(shoeCompare.realWorldPerformance.product1.breathability > 0, 'Must have breathability metric');
assert.ok(shoeCompare.realWorldPerformance.product1.durability > 0, 'Must have durability metric');

// Verify metric labels
const metricLabels = shoeCompare.categoryProfile.metrics.map(m => m.label);
assert.ok(!metricLabels.includes('Battery Backup'), 'Must not have Battery Backup label');
assert.ok(!metricLabels.includes('Thermal Control'), 'Must not have Thermal Control label');
assert.ok(!metricLabels.includes('Gaming Performance'), 'Must not have Gaming Performance label');
assert.ok(!metricLabels.includes('Camera Quality'), 'Must not have Camera Quality label');
assert.ok(metricLabels.some(l => l.includes('Comfort')), 'Must include Comfort');
assert.ok(metricLabels.some(l => l.includes('Grip')), 'Must include Grip');
assert.ok(metricLabels.some(l => l.includes('Cushioning')), 'Must include Cushioning');

// Verify pros and cons do not mention screen-on or camera
const p1ProsStr = shoeCompare.prosAndCons.product1.pros.join(' ');
assert.ok(!p1ProsStr.includes('screen-on'), 'Pros must not mention screen-on time for shoes');
assert.ok(!p1ProsStr.includes('camera'), 'Pros must not mention camera for shoes');
assert.ok(!p1ProsStr.includes('gaming'), 'Pros must not mention gaming for shoes');

// Verify regional intel
assert.ok(!shoeCompare.indiaIntel.product1.motherboardIssues.note.includes('motherboard'), 'Must not mention motherboard issues for shoes');
assert.ok(!shoeCompare.indiaIntel.product1.exchangeOffers.note.includes('phone'), 'Must not mention phone exchange for shoes');
console.log('✓ PASS: Footwear comparison verified with zero electronics leakage.\n');

// 2. Electronics Regression Test
console.log('Test 2: Testing Smartphone vs Smartphone (iPhone 18 Pro Max vs Galaxy S24 Ultra)...');
const iphone = {
  id: 1,
  name: 'Apple iPhone 18 Pro Max (256 GB, Deep Blue)',
  brand: 'Apple',
  category: 'Smartphones',
  rating: 4.8,
  totalReviews: 12450,
  bestPrice: 179900,
  originalPrice: 179900,
  dealScore: 92,
  specs: { RAM: '12 GB', Storage: '256 GB', Battery: '4852 mAh' },
  features: ["smartphone"],
  prices: [{ platform: "amazon", price: 179900, original: 179900, delivery: 1, rating: 4.8, currency: "INR" }]
};

const galaxy = {
  id: 2,
  name: 'Samsung Galaxy S24 Ultra (512 GB, Titanium Gray)',
  brand: 'Samsung',
  category: 'Smartphones',
  rating: 4.7,
  totalReviews: 8900,
  bestPrice: 129999,
  originalPrice: 139999,
  dealScore: 88,
  specs: { RAM: '12 GB', Storage: '512 GB', Battery: '5000 mAh' },
  features: ["smartphone"],
  prices: [{ platform: "amazon", price: 129999, original: 139999, delivery: 1, rating: 4.7, currency: "INR" }]
};

const phoneCompare = generateDeepCompareData(iphone, galaxy, 0);

assert.strictEqual(phoneCompare.categoryProfile.id, 'ELECTRONICS', 'Profile must be ELECTRONICS');
assert.strictEqual(phoneCompare.categoryProfile.subtitle, 'Simulated benchmarks based on brand DNA and user feedback');
assert.ok(phoneCompare.realWorldPerformance.product1.battery > 0, 'Electronics must preserve battery');
assert.ok(phoneCompare.realWorldPerformance.product1.heating > 0, 'Electronics must preserve heating');
assert.ok(phoneCompare.realWorldPerformance.product1.gaming > 0, 'Electronics must preserve gaming');
assert.ok(phoneCompare.realWorldPerformance.product1.camera > 0, 'Electronics must preserve camera');
console.log('✓ PASS: Electronics comparison strictly preserved.\n');

// 3. Apparel Test
console.log('Test 3: Testing Apparel vs Apparel...');
const tshirt1 = { id: 301, name: 'Campus Sutra Men Self Design Cotton T-shirt', brand: 'Campus Sutra', category: 'Clothing', rating: 4.4, totalReviews: 21900, bestPrice: 611, originalPrice: 1699, dealScore: 90 };
const tshirt2 = { id: 302, name: 'Puma Men Polo T-shirt', brand: 'Puma', category: 'Clothing', rating: 4.3, totalReviews: 450, bestPrice: 1199, originalPrice: 1999, dealScore: 84 };
const apparelCompare = generateDeepCompareData(tshirt1, tshirt2, 0);

assert.strictEqual(apparelCompare.categoryProfile.id, 'APPAREL');
assert.strictEqual(apparelCompare.realWorldPerformance.product1.battery, undefined);
assert.ok(apparelCompare.categoryProfile.metrics.some(m => m.label.includes('Comfort') || m.label.includes('Fabric')));
console.log('✓ PASS: Apparel comparison verified.\n');

// 4. Beauty Test
console.log('Test 4: Testing Beauty vs Beauty...');
const perf1 = { id: 401, name: 'Wild stone Men Edge EDP 100 ml', brand: 'Wild Stone', category: 'Beauty', rating: 4.5, totalReviews: 56000, bestPrice: 381, originalPrice: 699, dealScore: 95 };
const perf2 = { id: 402, name: 'SKINN Men Raw Eau De Parfum 50 ml', brand: 'SKINN', category: 'Beauty', rating: 4.4, totalReviews: 12000, bestPrice: 1895, originalPrice: 2495, dealScore: 82 };
const beautyCompare = generateDeepCompareData(perf1, perf2, 0);

assert.strictEqual(beautyCompare.categoryProfile.id, 'BEAUTY');
assert.strictEqual(beautyCompare.realWorldPerformance.product1.battery, undefined);
assert.ok(beautyCompare.categoryProfile.metrics.some(m => m.label.includes('Longevity') || m.label.includes('Sillage') || m.label.includes('Finish')));
console.log('✓ PASS: Beauty comparison verified.\n');

// 5. Cross-Category Compatibility Test
console.log('Test 5: Testing Cross-Category Compatibility Warning...');
const crossCheck = areCategoriesCompatible('Shoes', 'Smartphones', 'Campus Men Sneakers', 'iPhone 18 Pro Max');
assert.strictEqual(crossCheck.isCompatible, false, 'Shoes and Smartphones must not be mutually compatible');
assert.ok(crossCheck.warning.includes('Cross-category comparison'));
console.log('✓ PASS: Cross-category warning triggered correctly.\n');

console.log('====================================================');
console.log('ALL FRONTEND VERIFICATION TESTS PASSED SUCCESSFULLY!');
console.log('====================================================');
