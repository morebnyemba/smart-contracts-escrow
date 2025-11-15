'use client';

import { useState, useEffect } from 'react';
import styles from './page.module.css';
import { searchAPI, categoriesAPI, SellerSearchResult, ServiceCategory } from '@/lib/api';

interface DisplaySeller {
  id: string;
  name: string;
  company: string | null;
  skills: string[];
  verified: boolean;
  rating?: number;
}

export default function FindSeller() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [verifiedOnly] = useState(true); // API only returns verified sellers
  const [sellers, setSellers] = useState<DisplaySeller[]>([]);
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // Fetch categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      const response = await categoriesAPI.getAll();
      if (response.data) {
        setCategories(response.data);
      }
    };
    fetchCategories();
  }, []);

  // Fetch sellers based on selected category
  useEffect(() => {
    const fetchSellers = async () => {
      if (!selectedCategory) {
        setSellers([]);
        return;
      }

      setLoading(true);
      setError('');

      try {
        const response = await searchAPI.searchSellers(selectedCategory);
        
        if (response.error) {
          setError(response.error);
          setSellers([]);
        } else if (response.data) {
          // Map API response to display format
          const mapped = response.data.map((seller: SellerSearchResult) => ({
            id: seller.public_seller_id,
            name: seller.username,
            company: seller.company_name || null,
            skills: seller.skills.map(s => s.name),
            verified: seller.verification_status === 'VERIFIED',
            rating: undefined, // API doesn't provide rating yet
          }));
          setSellers(mapped);
        }
      } catch (err) {
        setError('Failed to search sellers');
        console.error('Error searching sellers:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSellers();
  }, [selectedCategory]);

  // Filter sellers based on search query
  const filteredSellers = sellers.filter((seller) => {
    const matchesSearch = searchQuery === '' || 
      seller.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      seller.company?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      seller.skills.some(skill => skill.toLowerCase().includes(searchQuery.toLowerCase()));
    
    return matchesSearch;
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
              <option value="">Select a category to search</option>
              {categories.map((category) => (
                <option key={category.slug} value={category.slug}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.filterGroup}>
            <label>
              <input
                type="checkbox"
                checked={verifiedOnly}
                disabled={true}
                className={styles.checkbox}
              />
              Verified sellers only (all results are verified)
            </label>
          </div>
        </div>
      </div>

      {loading && (
        <div className={styles.results}>
          <p className={styles.resultCount}>Loading sellers...</p>
        </div>
      )}

      {error && (
        <div className={styles.results}>
          <p className={styles.resultCount} style={{ color: 'red' }}>{error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className={styles.results}>
          {selectedCategory ? (
            <>
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
                    
                    {seller.rating && (
                      <div className={styles.rating}>
                        <span className={styles.stars}>★</span>
                        <span>{seller.rating.toFixed(1)}</span>
                      </div>
                    )}
                    
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
                  <p>Try adjusting your search or selecting a different category.</p>
                </div>
              )}
            </>
          ) : (
            <div className={styles.noResults}>
              <p>Please select a category to search for sellers.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
