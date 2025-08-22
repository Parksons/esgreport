import React from 'react';
import { useSecurity } from '../context/SecurityContext';
import ImageGallery from '../components/ImageGallery';
import './Home.css';

const Home = () => {
  return (
    <div className="home-page">
      {/* Hero Image Section - Outside content container */}
      <div className="hero-image-section">
        <img 
          src="public/images/hero/hero-banner.jpg" 
          alt="Hero Banner" 
          className="hero-image"
        />
      </div>

      {/* Content Container - Only for ESG and Gallery sections */}
      <div className="content-container fade-in">
        {/* ESG Section */}
        <div className="esg-section">
          <h1 className="esg-title">Building a Sustainable Future: Our Commitment to Environmental, Social & Governance Leadership</h1>
          
          <div className="esg-text">
            <p>
              Parksons Packaging, India's largest folding carton manufacturer and a leader in sustainable packaging, proudly presents our inaugural ESG Report for 2023-24. This milestone marks our firm commitment to transparency, responsible growth, and driving positive impact across our industry and communities.
            </p>
            <p>
              We thank our stakeholders for joining us as we embark on this journey toward a more sustainable and innovative future.
            </p>
          </div>
        </div>

        {/* Image Gallery Section */}
        <div className="gallery-section">
          <ImageGallery />
        </div>
      </div>
    </div>
  );
};

export default Home;
