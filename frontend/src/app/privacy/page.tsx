import styles from './privacy.module.css';

export default function PrivacyPolicy() {
  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Privacy Policy</h1>
        <div className={styles.lastUpdated}>Last Updated: November 15, 2025</div>

        <div className={styles.content}>
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>1. Introduction</h2>
            <p className={styles.paragraph}>
              Welcome to Smart Contracts Escrow Platform. We are committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our escrow platform.
            </p>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>2. Information We Collect</h2>
            <h3 className={styles.subsectionTitle}>2.1 Personal Information</h3>
            <p className={styles.paragraph}>
              When you register for an account, we collect:
            </p>
            <ul className={styles.list}>
              <li>Full name and username</li>
              <li>Email address</li>
              <li>Contact information</li>
              <li>Company information (for business accounts)</li>
            </ul>

            <h3 className={styles.subsectionTitle}>2.2 Transaction Information</h3>
            <p className={styles.paragraph}>
              We collect information related to your transactions:
            </p>
            <ul className={styles.list}>
              <li>Transaction details and amounts</li>
              <li>Milestone information</li>
              <li>Payment information</li>
              <li>Communication between parties</li>
            </ul>

            <h3 className={styles.subsectionTitle}>2.3 Technical Information</h3>
            <p className={styles.paragraph}>
              We automatically collect certain technical information:
            </p>
            <ul className={styles.list}>
              <li>IP address and browser type</li>
              <li>Device information</li>
              <li>Usage data and analytics</li>
              <li>Cookies and similar tracking technologies</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>3. How We Use Your Information</h2>
            <p className={styles.paragraph}>
              We use your information for the following purposes:
            </p>
            <ul className={styles.list}>
              <li>To provide and maintain our escrow services</li>
              <li>To process transactions and manage accounts</li>
              <li>To communicate with you about your transactions</li>
              <li>To improve our platform and user experience</li>
              <li>To detect and prevent fraud and security threats</li>
              <li>To comply with legal obligations</li>
              <li>To send important updates and notifications</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>4. Information Sharing and Disclosure</h2>
            <p className={styles.paragraph}>
              We do not sell your personal information. We may share your information in the following circumstances:
            </p>
            <ul className={styles.list}>
              <li><strong>With Transaction Parties:</strong> Information necessary to complete transactions is shared between buyers and sellers</li>
              <li><strong>Service Providers:</strong> We may share information with third-party service providers who perform services on our behalf</li>
              <li><strong>Legal Requirements:</strong> We may disclose information when required by law or to protect our rights</li>
              <li><strong>Business Transfers:</strong> In the event of a merger, acquisition, or sale of assets</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>5. Data Security</h2>
            <p className={styles.paragraph}>
              We implement appropriate technical and organizational security measures to protect your information:
            </p>
            <ul className={styles.list}>
              <li>Encryption of data in transit and at rest</li>
              <li>Secure authentication mechanisms</li>
              <li>Regular security audits and updates</li>
              <li>Access controls and monitoring</li>
              <li>Secure data storage infrastructure</li>
            </ul>
            <p className={styles.paragraph}>
              However, no method of transmission over the internet is 100% secure, and we cannot guarantee absolute security.
            </p>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>6. Your Rights and Choices</h2>
            <p className={styles.paragraph}>
              You have the following rights regarding your personal information:
            </p>
            <ul className={styles.list}>
              <li><strong>Access:</strong> Request access to your personal information</li>
              <li><strong>Correction:</strong> Request correction of inaccurate information</li>
              <li><strong>Deletion:</strong> Request deletion of your information (subject to legal obligations)</li>
              <li><strong>Data Portability:</strong> Request a copy of your data in a portable format</li>
              <li><strong>Opt-Out:</strong> Opt out of marketing communications</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>7. Cookies and Tracking Technologies</h2>
            <p className={styles.paragraph}>
              We use cookies and similar technologies to:
            </p>
            <ul className={styles.list}>
              <li>Maintain your session and authentication</li>
              <li>Remember your preferences</li>
              <li>Analyze usage patterns and improve our services</li>
              <li>Provide personalized experiences</li>
            </ul>
            <p className={styles.paragraph}>
              You can control cookies through your browser settings, but disabling cookies may affect functionality.
            </p>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>8. Data Retention</h2>
            <p className={styles.paragraph}>
              We retain your information for as long as necessary to:
            </p>
            <ul className={styles.list}>
              <li>Provide our services and maintain your account</li>
              <li>Comply with legal and regulatory requirements</li>
              <li>Resolve disputes and enforce agreements</li>
              <li>Maintain transaction records for business purposes</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>9. Children&apos;s Privacy</h2>
            <p className={styles.paragraph}>
              Our platform is not intended for users under the age of 18. We do not knowingly collect information from children under 18. If you believe we have collected information from a child, please contact us immediately.
            </p>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>10. International Data Transfers</h2>
            <p className={styles.paragraph}>
              Your information may be transferred to and processed in countries other than your country of residence. We ensure appropriate safeguards are in place to protect your information in accordance with this Privacy Policy.
            </p>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>11. Changes to This Privacy Policy</h2>
            <p className={styles.paragraph}>
              We may update this Privacy Policy from time to time. We will notify you of any significant changes by posting the new Privacy Policy on this page and updating the &quot;Last Updated&quot; date. Your continued use of the platform after changes are posted constitutes your acceptance of the revised policy.
            </p>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>12. Contact Us</h2>
            <p className={styles.paragraph}>
              If you have any questions, concerns, or requests regarding this Privacy Policy or our privacy practices, please contact us at:
            </p>
            <div className={styles.contactInfo}>
              <p><strong>Email:</strong> privacy@smartcontractsescrow.net</p>
              <p><strong>Platform:</strong> Smart Contracts Escrow Platform</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
