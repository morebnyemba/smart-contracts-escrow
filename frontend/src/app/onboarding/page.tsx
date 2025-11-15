'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { sellerAPI, categoriesAPI, ServiceCategory, CreateSellerProfileData } from '@/lib/api';
import { useUserStore } from '@/store/userStore';
import styles from './onboarding.module.css';

export default function SellerOnboarding() {
  const router = useRouter();
  const user = useUserStore((state) => state.user);
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [formData, setFormData] = useState<CreateSellerProfileData>({
    account_type: 'INDIVIDUAL',
    company_name: '',
    skill_ids: [],
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);

  useEffect(() => {
    // Check if user is authenticated
    if (!user) {
      router.push('/auth/login');
      return;
    }

    // Check if already a seller
    if (user.is_seller) {
      router.push('/dashboard');
      return;
    }

    // Load categories
    const loadCategories = async () => {
      const result = await categoriesAPI.getAll();
      if (result.data) {
        setCategories(result.data);
      }
    };
    
    loadCategories();
  }, [user, router]);

  const handleAccountTypeChange = (type: 'INDIVIDUAL' | 'COMPANY') => {
    setFormData({
      ...formData,
      account_type: type,
      company_name: type === 'INDIVIDUAL' ? '' : formData.company_name,
    });
  };

  const handleSkillToggle = (categoryId: number) => {
    const currentSkills = formData.skill_ids || [];
    const isSelected = currentSkills.includes(categoryId);
    
    setFormData({
      ...formData,
      skill_ids: isSelected
        ? currentSkills.filter((id) => id !== categoryId)
        : [...currentSkills, categoryId],
    });
  };

  const handleNext = () => {
    if (step === 1 && formData.account_type === 'COMPANY' && !formData.company_name) {
      setError('Please enter your company name');
      return;
    }
    setError('');
    setStep(2);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!formData.skill_ids || formData.skill_ids.length === 0) {
      setError('Please select at least one skill');
      return;
    }

    setLoading(true);

    const result = await sellerAPI.createProfile(formData);
    
    if (result.error) {
      setError(result.error);
      setLoading(false);
      return;
    }

    // Success - refresh user data and redirect
    router.push('/dashboard');
  };

  if (!user) {
    return null;
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Become a Seller</h1>
        <div className={styles.steps}>
          <div className={`${styles.stepIndicator} ${step >= 1 ? styles.active : ''}`}>
            1. Account Type
          </div>
          <div className={`${styles.stepIndicator} ${step >= 2 ? styles.active : ''}`}>
            2. Skills
          </div>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        {step === 1 && (
          <div className={styles.stepContent}>
            <h2 className={styles.subtitle}>Choose your account type</h2>
            
            <div className={styles.accountTypes}>
              <button
                type="button"
                className={`${styles.accountTypeCard} ${
                  formData.account_type === 'INDIVIDUAL' ? styles.selected : ''
                }`}
                onClick={() => handleAccountTypeChange('INDIVIDUAL')}
              >
                <h3>Individual</h3>
                <p>For freelancers and solo professionals</p>
              </button>

              <button
                type="button"
                className={`${styles.accountTypeCard} ${
                  formData.account_type === 'COMPANY' ? styles.selected : ''
                }`}
                onClick={() => handleAccountTypeChange('COMPANY')}
              >
                <h3>Company</h3>
                <p>For businesses and agencies</p>
              </button>
            </div>

            {formData.account_type === 'COMPANY' && (
              <div className={styles.formGroup}>
                <label htmlFor="company_name">Company Name</label>
                <input
                  type="text"
                  id="company_name"
                  value={formData.company_name}
                  onChange={(e) =>
                    setFormData({ ...formData, company_name: e.target.value })
                  }
                  className={styles.input}
                  required
                />
              </div>
            )}

            <button onClick={handleNext} className={styles.button}>
              Next
            </button>
          </div>
        )}

        {step === 2 && (
          <form onSubmit={handleSubmit} className={styles.stepContent}>
            <h2 className={styles.subtitle}>Select your skills</h2>
            <p className={styles.description}>Choose the services you can provide</p>

            <div className={styles.skillsGrid}>
              {categories.map((category) => (
                <button
                  key={category.id}
                  type="button"
                  className={`${styles.skillCard} ${
                    formData.skill_ids?.includes(category.id) ? styles.selected : ''
                  }`}
                  onClick={() => handleSkillToggle(category.id)}
                >
                  {category.name}
                </button>
              ))}
            </div>

            <div className={styles.buttonGroup}>
              <button
                type="button"
                onClick={() => setStep(1)}
                className={styles.buttonSecondary}
              >
                Back
              </button>
              <button
                type="submit"
                disabled={loading}
                className={styles.button}
              >
                {loading ? 'Creating profile...' : 'Complete Setup'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
