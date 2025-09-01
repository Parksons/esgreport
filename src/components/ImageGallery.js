import React, { useState, useEffect } from 'react';
import { useSecurity } from '../context/SecurityContext';
import { galleryImages } from '../data/galleryData';
import AccessForm from './AccessForm';
import './ImageGallery.css';

const ImageGallery = () => {
  const { isAuthenticated, userData } = useSecurity();
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showAccessForm, setShowAccessForm] = useState(false);
  const [hasAccess, setHasAccess] = useState(false);

  // Check if user is already authenticated
  useEffect(() => {
    if (isAuthenticated && userData) {
      setHasAccess(true);
    }
  }, [isAuthenticated, userData]);

  const goToPreviousSlide = () => {
    if (currentSlide > 0) {
      setCurrentSlide(currentSlide - 1);
    }
  };

  const goToNextSlide = () => {
    // Check if user has access or if we're within the first 3 slides
    if (hasAccess || currentSlide < 2) {
      if (currentSlide < galleryImages.length - 1) {
        setCurrentSlide(currentSlide + 1);
      }
    } else {
      // Show access form when trying to go beyond slide 3
      setShowAccessForm(true);
    }
  };

  const handleAccessSuccess = () => {
    setHasAccess(true);
    // Continue to the next slide after successful access
    if (currentSlide < galleryImages.length - 1) {
      setCurrentSlide(currentSlide + 1);
    }
  };

  const handleCloseForm = () => {
    setShowAccessForm(false);
  };

  if (galleryImages.length === 0) {
    return <div className="image-gallery-placeholder">No images to display.</div>;
  }

  return (
    <>
      <div className="image-gallery">
        <div className="gallery-container">
          <div className="gallery-slides">
            <div className="gallery-slide active">
              <img
                src={galleryImages[currentSlide].src}
                alt={galleryImages[currentSlide].alt}
                className="gallery-image"
              />
            </div>
          </div>

          {/* Navigation Arrows Only */}
          <button 
            className="gallery-nav prev" 
            onClick={goToPreviousSlide} 
            disabled={currentSlide === 0}
            aria-label="Previous slide"
          >
            ‹
          </button>
          <button 
            className="gallery-nav next" 
            onClick={goToNextSlide} 
            disabled={currentSlide === galleryImages.length - 1}
            aria-label="Next slide"
          >
            ›
          </button>
        </div>
      </div>

      {/* Access Form Modal */}
      <AccessForm
        isOpen={showAccessForm}
        onClose={handleCloseForm}
        onSuccess={handleAccessSuccess}
      />
    </>
  );
};

export default ImageGallery;
