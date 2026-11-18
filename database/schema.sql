-- ============================================================
-- AI-Powered Food Waste Prediction System
-- MySQL Database Schema
-- Target: College Mess Operations & Food Waste Reduction
-- ============================================================

CREATE DATABASE IF NOT EXISTS food_waste_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE food_waste_db;

-- 1. Table for Daily Mess Records (Attendance, Prepared Meals, Consumed, Waste, and Prediction Integration)
CREATE TABLE IF NOT EXISTS mess_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_date DATE NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    meal_type VARCHAR(20) NOT NULL, -- Breakfast, Lunch, Snacks, Dinner
    menu_name VARCHAR(100) NOT NULL,
    attendance INT NOT NULL,
    prepared_meals INT NOT NULL,
    consumed_meals INT NULL, -- NULL if meal is currently ongoing
    wasted_meals INT NULL, -- Actual Food Waste = prepared_meals - consumed_meals
    waste_percentage DECIMAL(5,2) NULL,
    predicted_meals INT NULL, -- AI Predicted Demand from ML model
    estimated_surplus INT NULL, -- Estimated Surplus Before Prep = prepared_meals - predicted_meals
    prediction_error INT NULL, -- Prediction Error = consumed_meals - predicted_meals
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_record_date (record_date),
    INDEX idx_meal_type (meal_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Table for AI Prediction History
CREATE TABLE IF NOT EXISTS prediction_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prediction_date DATE NOT NULL,
    meal_type VARCHAR(20) NOT NULL,
    menu_name VARCHAR(100) NOT NULL,
    expected_attendance INT NOT NULL,
    predicted_meals INT NOT NULL,
    confidence_interval_min INT,
    confidence_interval_max INT,
    model_version VARCHAR(50) DEFAULT 'RandomForestRegressor_v1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Table for Surplus Food Verification & Advisory
CREATE TABLE IF NOT EXISTS surplus_advisories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT,
    date DATE NOT NULL,
    meal_type VARCHAR(20) NOT NULL,
    surplus_quantity INT NOT NULL,
    status ENUM('Pending Review', 'Safe for Donation', 'Self-Consumed/Composted', 'Discarded') DEFAULT 'Pending Review',
    food_safety_verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(100),
    recipient_organization VARCHAR(150),
    advisory_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES mess_records(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
