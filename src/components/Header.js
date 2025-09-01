import React, { useState, useEffect } from 'react';
import { useSecurity } from '../context/SecurityContext';
import './Header.css';

const Header = ({ currentPage, onPageChange }) => {
  const { isAuthenticated, userData, logout } = useSecurity();
  const [openDropdown, setOpenDropdown] = useState(null);
  const [isHeaderVisible, setIsHeaderVisible] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const galleryElement = document.querySelector('.gallery-section');
      if (galleryElement) {
        const galleryRect = galleryElement.getBoundingClientRect();
        const headerHeight = 80; // Approximate header height
        
        // Hide header when gallery is in view (considering header height)
        if (galleryRect.top <= headerHeight) {
          setIsHeaderVisible(false);
        } else {
          setIsHeaderVisible(true);
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
    setOpenDropdown(null);
  };

  const pages = [
    { id: 'home', name: 'Home', path: '/', hasDropdown: false, url: 'https://parksonspackaging.com/' },
    { 
      id: 'about', 
      name: 'About', 
      path: '/about', 
      hasDropdown: true,
      url: 'https://parksonspackaging.com/about/',
      submenu: [
        { name: 'Company Background', path: '/about/background', url: 'https://parksonspackaging.com/about/company-background/' },
        { name: 'Management Team', path: '/about/team', url: 'https://parksonspackaging.com/about/management-team/' },
        { name: 'Sustainability', path: '/about/sustainability', url: 'https://parksonspackaging.com/about/sustainability/' },
        { name: 'CSR', path: '/about/csr', url: 'https://parksonspackaging.com/about/csr/' },
        { name: 'Quality & Certifications', path: '/about/quality', url: 'https://parksonspackaging.com/about/quality-and-certifications/' },
        { name: 'Awards & Client Recognition', path: '/about/awards', url: 'https://parksonspackaging.com/awards-client-recognition/' },
        { name: 'News', path: '/about/news', url: 'https://parksonspackaging.com/news/' }
      ]
    },
    { 
      id: 'innovation', 
      name: 'Innovation and Technology', 
      path: '/innovation', 
      hasDropdown: true,
      url: 'https://parksonspackaging.com/innovation-and-technology/',
      submenu: [
        { name: 'Innovation', path: '/innovation/innovation', url: 'https://parksonspackaging.com/innovation-and-technology/innovation/' },
        { name: 'Design', path: '/innovation/design', url: 'https://parksonspackaging.com/innovation-and-technology/design/' },
        { name: 'Printing Technology', path: '/innovation/printing', url: 'https://parksonspackaging.com/innovation-and-technology/printing-technology/' },
        { name: 'Finishing Technology', path: '/innovation/finishing', url: 'https://parksonspackaging.com/innovation-and-technology/finishing-technology/' }
      ]
    },
    { 
      id: 'markets', 
      name: 'Markets and Products', 
      path: '/markets', 
      hasDropdown: true,
      url: 'https://parksonspackaging.com/markets-and-products/',
      submenu: {
        columns: [
          {
            title: 'Our Markets',
            items: [
              { name: 'Consumer Goods', path: '/markets/consumer-goods', url: 'https://parksonspackaging.com/our-markets/consumer-goods/' },
              { name: 'Healthcare', path: '/markets/healthcare', url: 'https://parksonspackaging.com/our-markets/healthcare/' },
              { name: 'Gable Top Packaging', path: '/markets/gable-top', url: 'https://parksonspackaging.com/our-markets/gable-top-packaging/' },
              { name: 'Food Service', path: '/markets/food-service', url: 'https://parksonspackaging.com/our-markets/food-service/' },
              { name: 'International', path: '/markets/international', url: 'https://parksonspackaging.com/our-markets/international/' }
            ]
          },
          {
            title: 'Our Products',
            items: [
              { name: 'Folding Cartons', path: '/markets/folding-cartons', url: 'https://parksonspackaging.com/our-products/folding-cartons/' },
              { name: 'Gable Top Cartons', path: '/markets/gable-top-cartons', url: 'https://parksonspackaging.com/our-products/gable-top-cartons/' },
              { name: 'Speciality Packaging', path: '/markets/speciality', url: 'https://parksonspackaging.com/our-products/speciality-packaging/' },
              { name: 'Litho Lam', path: '/markets/litho-lam', url: 'https://parksonspackaging.com/our-products/litho-lam/' },
              { name: 'Rigid Box', path: '/markets/rigid-box', url: 'https://parksonspackaging.com/our-products/rigid-box/' },
              { name: 'Canister', path: '/markets/canister', url: 'https://parksonspackaging.com/our-products/canister/' },
              { name: 'Paper Pod', path: '/markets/paper-pod', url: 'https://parksonspackaging.com/our-products/paper-pod/' }
            ]
          }
        ]
      }
    },
    { id: 'locations', name: 'Locations', path: '/locations', hasDropdown: false, url: 'https://parksonspackaging.com/locations/' },
    { id: 'careers', name: 'Careers', path: '/careers', hasDropdown: false, url: 'https://parksonspackaging.com/careers/' }
  ];

  const handleMouseEnter = (pageId) => {
    if (pages.find(p => p.id === pageId)?.hasDropdown) {
      setOpenDropdown(pageId);
    }
  };

  const handleMouseLeave = () => {
    setOpenDropdown(null);
  };

  const handlePageChange = (page) => {
    onPageChange(page);
    setOpenDropdown(null);
  };

  const handleDropdownToggle = (pageId) => {
    setOpenDropdown(openDropdown === pageId ? null : pageId);
  };

  return (
    <header className={`header ${!isHeaderVisible ? 'hidden' : ''}`}>
      <div className="header-container">
        {/* Company Logo Section */}
        <div className="logo-section">
          <img 
            src="/parksons-logo-1-190x44.png" 
            alt="Parksons Packaging LTD" 
            className="logo-image"
          />
        </div>
        
        {/* Mobile Toggle Button */}
        <button 
          className="mobile-toggle"
          onClick={toggleMobileMenu}
          aria-label="Toggle mobile menu"
        >
          <span className={`hamburger ${isMobileMenuOpen ? 'open' : ''}`}></span>
        </button>
        
        {/* Navigation Section */}
        <div className={`nav-section ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
          <nav className="nav">
            {pages.map((page) => (
              <div 
                key={page.id} 
                className="nav-item"
                onMouseEnter={() => handleMouseEnter(page.id)}
                onMouseLeave={handleMouseLeave}
              >
                <button
                  className={`nav-link ${currentPage === page.id ? 'active' : ''}`}
                  onClick={() => {
                    if (page.hasDropdown) {
                      handleDropdownToggle(page.id);
                    } else {
                      window.open(page.url, '_blank');
                      closeMobileMenu();
                    }
                  }}
                >
                  {page.name}
                  {page.hasDropdown && <span className="dropdown-icon">▼</span>}
                </button>
                
                {/* Dropdown Submenu */}
                {page.hasDropdown && page.submenu && openDropdown === page.id && (
                  <div className="dropdown-menu">
                    {/* Handle simple array format (About, Innovation) */}
                    {Array.isArray(page.submenu) && page.submenu.map((subItem, index) => (
                      <a
                        key={index}
                        href={subItem.url}
                        className="dropdown-item"
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={closeMobileMenu}
                      >
                        {subItem.name}
                      </a>
                    ))}
                    
                    {/* Handle columns format (Markets and Products) */}
                    {page.submenu.columns && page.submenu.columns.map((column, colIndex) => (
                      <div key={colIndex} className="dropdown-column">
                        {column.title && <h3>{column.title}</h3>}
                        <ul>
                          {column.items.map((item, index) => (
                            <li key={index}>
                              <a
                                href={item.url}
                                className="dropdown-item"
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={closeMobileMenu}
                              >
                                {item.name}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            <button 
              className="contact-btn"
              onClick={() => {
                window.open('https://parksonspackaging.com/contact/', '_blank');
                closeMobileMenu();
              }}
            >
              Contact
            </button>
          </nav>

          <div className="user-info">
            {isAuthenticated && userData && (
              <div className="user-section">
                <span className="user-name">Welcome, {userData.name}</span>
                <button 
                  className="logout-btn"
                  onClick={() => {
                    logout();
                    closeMobileMenu();
                  }}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
