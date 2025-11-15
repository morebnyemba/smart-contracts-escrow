'use client';

import { useState } from 'react';
import styles from './page.module.css';

// Mock data for sellers - replace with API call when backend is ready
const mockSellers = [
  {
    id: '1',
    name: 'John Developer',
    company: 'Tech Solutions Inc',
    skills: ['Web Development', 'React', 'Node.js'],
    verified: true,
    rating: 4.8,
  },
  {
    id: '2',
    name: 'Jane Designer',
    company: null,
    skills: ['UI/UX Design', 'Graphic Design', 'Branding'],
    verified: true,
    rating: 4.9,
  },
  {
    id: '3',
    name: 'Mike Consultant',
    company: 'Consulting Group LLC',
    skills: ['Business Strategy', 'Marketing', 'Sales'],
    verified: false,
    rating: 4.5,
  },
  {
    id: '4',
    name: 'Sarah Engineer',
    company: null,
    skills: ['Backend Development', 'Python', 'Database Design'],
    verified: true,
    rating: 4.7,
  },
];

const serviceCategories = [
  'Web Development',
  'Mobile Development',
  'UI/UX Design',
  'Graphic Design',
  'Content Writing',
  'Marketing',
  'Business Strategy',
  'Data Analysis',
];

export default function FindSeller() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [verifiedOnly, setVerifiedOnly] = useState(false);

  // Filter sellers based on search criteria
  const filteredSellers = mockSellers.filter((seller) => {
    const matchesSearch = searchQuery === '' || 
      seller.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      seller.company?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      seller.skills.some(skill => skill.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === '' || 
      seller.skills.includes(selectedCategory);
    
    const matchesVerified = !verifiedOnly || seller.verified;
    
    return matchesSearch && matchesCategory && matchesVerified;
  });

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Find a Seller</h1>
        <p>Search for verified sellers by skill, name, or company</p>
      </header>

      <div className={styles.searchSection}>
        <div className={styles.searchBar}>
          <input
            type="text"
            placeholder="Search by name, skill, or company..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={styles.searchInput}
          />
        </div>

        <div className={styles.filters}>
          <div className={styles.filterGroup}>
            <label htmlFor="category">Category:</label>
            <select
              id="category"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className={styles.select}
            >
              <option value="">All Categories</option>
              {serviceCategories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.filterGroup}>
            <label>
              <input
                type="checkbox"
                checked={verifiedOnly}
                onChange={(e) => setVerifiedOnly(e.target.checked)}
                className={styles.checkbox}
              />
              Verified sellers only
            </label>
          </div>
        </div>
      </div>

      <div className={styles.results}>
        <p className={styles.resultCount}>
          {filteredSellers.length} seller{filteredSellers.length !== 1 ? 's' : ''} found
        </p>

        <div className={styles.sellerGrid}>
          {filteredSellers.map((seller) => (
            <div key={seller.id} className={styles.sellerCard}>
              <div className={styles.sellerHeader}>
                <h3>{seller.name}</h3>
                {seller.verified && (
                  <span className={styles.verifiedBadge}>✓ Verified</span>
                )}
              </div>
              
              {seller.company && (
                <p className={styles.company}>{seller.company}</p>
              )}
              
              <div className={styles.rating}>
                <span className={styles.stars}>★</span>
                <span>{seller.rating.toFixed(1)}</span>
              </div>
              
              <div className={styles.skills}>
                {seller.skills.map((skill) => (
                  <span key={skill} className={styles.skillTag}>
                    {skill}
                  </span>
                ))}
              </div>
              
              <button className={styles.contactButton}>
                Contact Seller
              </button>
            </div>
          ))}
        </div>

        {filteredSellers.length === 0 && (
          <div className={styles.noResults}>
            <p>No sellers found matching your criteria.</p>
            <p>Try adjusting your search or filters.</p>
          </div>
        )}
      </div>
    </div>
  );
}
