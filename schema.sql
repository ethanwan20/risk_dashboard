CREATE DATABASE IF NOT EXISTS risk_dashboard;
USE risk_dashboard;

-- Table: portfolios 

CREATE TABLE IF NOT EXISTS portfolios(
	id INT 	AUTO_INCREMENT PRIMARY KEY, 
    portfolio_name VARCHAR(100) NOT NULL,
    ticker VARCHAR(20) NOT NULL, 
	weight DECIMAL(6,4) NOT NULL, 
    UNIQUE KEY unique_portfolio_ticker (portfolio_name, ticker)
);

-- Table: prices

CREATE TABLE IF NOT EXISTS prices (
	id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    price_date DATE NOT NULL,
    close_price DECIMAL(12,4) NOT NULL,
    UNIQUE KEY unique_ticker_date (ticker, price_date)
);

-- Table: risk results

CREATE TABLE IF NOT EXISTS risk_results(
	id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_name VARCHAR(100) NOT NULL,
    run_date DATE NOT NULL,
    confidence_level DECIMAL(4,2) NOT NULL,
    method VARCHAR(20) NOT NULL, 
    var_value DECIMAL(14,2) NOT NULL, 
    expected_shortfall DECIMAL(14,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: scenarios

CREATE TABLE IF NOT EXISTS scenarios(
	id INT AUTO_INCREMENT PRIMARY KEY,
    scenario_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    description VARCHAR(255)

);

INSERT INTO scenarios (scenario_name, start_date, end_date, description) VALUES
	('2008 Financial Crisis', '2008-09-01', '2008-11-30', 'Lehman Brothers collapse and aftermath'),
    ('COVID-19 Crash', '2020-02-15', '2020-04-15', 'Pandemic driven market crash and initial recovery'),
    ('2020 Rate Hikes', '2022-01-01', '2022-10-31', 'Aggressive central bank rate hikes and bond/equity selloff');