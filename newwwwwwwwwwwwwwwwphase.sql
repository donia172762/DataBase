DROP DATABASE IF EXISTS labmart6_db;
CREATE DATABASE labmart6_db;
USE labmart6_db;

-- =========================
-- Branch
-- =========================
CREATE TABLE Branch (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    address VARCHAR(100) NOT NULL,
    phone VARCHAR(20)
);

INSERT INTO Branch (city, address, phone) VALUES
('Ramallah', 'Main Street', '0591239876'),
('Nablus', 'Downtown', '0592223344');

-- =========================
-- Product
-- =========================
CREATE TABLE Product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    brand VARCHAR(50),
    unit_price_sell DECIMAL(10,2) NOT NULL,
    unit_price_cost DECIMAL(10,2) NOT NULL,
    expiry_date DATE,
    image VARCHAR(255) NOT NULL
);
INSERT INTO Product
(product_name, category, brand, unit_price_sell, unit_price_cost, expiry_date, image)
VALUES
('Microscope', 'Optical', 'LabTech', 20000.00, 950.00, '2027-12-31', 'micro2.jpg'),
('ONiLAB Lab PRP Benchtop Centrifuge', 'Glassware', 'LabGlass', 800.00, 6.00, '2030-01-01', 'ONiLAB Lab PRP Benchtop Centrifuge.jpg'),
('Patient Monitors', 'Glassware', 'ChemPro', 12000.00, 15.00, '2030-01-01', 'Patient Monitors.jpg'),
('Compound Light Microscope', 'Glassware', 'LabGlass', 1800.00, 6.00, '2030-01-01', 'pb-50b_3_1_1-600x600.jpg'),
('pH Meter with Stand', 'Safety', 'SafeLab', 500.00, 7.00, '2032-06-30', 'q500-with-stand_large.jpg'),
('Welch Allyn LXI Spot Vital Signs Monitor (Model 45)', 'Glassware', 'LabGlass', 5000.00, 6.00, '2030-01-01', 'Welch Allyn LXI Spot 45 (NT0,MT0) Vital Signs Monitor NIBP BP SpO2 Temperature.jpg'),
('Stereo Microscope', 'Glassware', 'LabGlass', 1200.00, 6.00, '2030-01-01', 'mr.jpg'),
('Inverted Fluorescence Microscope', 'Glassware', 'LabGlass', 400000.00, 6.00, '2030-01-01', 'Zeiss AXIO Observer 7 Inverted LED Fluorescence Phase Contrast Motorized XY Microscope.jpg');
ALTER TABLE product
MODIFY image VARCHAR(255) NULL DEFAULT '';

-- =========================
-- Customer
-- =========================
CREATE TABLE Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    city VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

INSERT INTO Customer (customer_name, type, city, phone, email, password_hash) VALUES
('Birzeit University', 'University', 'Ramallah', '022987654', 'contact@birzeit.edu', 'hash1'),
('An-Najah University', 'University', 'Nablus', '092345678', 'info@najah.edu', 'hash2'),
('Al-Quds Research Center', 'Research Center', 'Jerusalem', '029876543', 'lab@aqrc.ps', 'hash3');

-- =========================
-- Warehouse
-- =========================
CREATE TABLE Warehouse (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    branch_id INT NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES Branch(branch_id)
);

INSERT INTO Warehouse (warehouse_name, location, phone, branch_id) VALUES
('Main Warehouse', 'Ramallah', '0599876543', 1),
('Chemicals Warehouse', 'Ramallah', '0598765432', 1),
('Equipment Warehouse', 'Nablus', '0597654321', 2);
INSERT INTO Warehouse (warehouse_name, location, phone, branch_id) VALUES
('Blood Glucose Meters', 'Ramallah', '067866666', 1),
('Pregnancy Test Devices', 'Ramallah', '9038839900', 1),
('Blood Pressure Monitors', 'Nablus', '008765430', 1),
('Medical Gloves', 'Nablus', '0987654321', 1),
('Small Medical Equipment', 'Nablus', '123456789', 1),
('Disinfectants', 'Nablus', '0000000000', 1),
('Nebulizers and Inhalation Devices', 'Ramallah', '0000000000', 1),
('Thermometers', 'Ramallah', '0000000000', 1),
('Medical Stethoscopes', 'Ramallah', '0000000000', 1),
('Hearing Aids', 'Ramallah', '0000000000', 1);
INSERT INTO Product 
(product_name, brand, unit_price_sell, unit_price_cost, expiry_date, image)
VALUES
('Blood Glucose Meter – AccuCheck Active', 'AccuCheck', 250.00, 180.00, '2030-12-31', 'Accu-Chek Active Blood Glucose Meter with 50 Test Strips and Fast Results.jpg'),
('Blood Glucose Meter – OneTouch Select', 'OneTouch', 230.00, 160.00, '2030-12-31', 'Abbott Freestyle Libre 2 No-Prick Blood Glucose Sensor Up to 14 Days.jpg'),
('Blood Glucose Meter – FreeStyle Lite', 'Abbott', 270.00, 190.00, '2030-12-31', 'Bayer Contour Next Blood Glucose Meter High Accuracy and Fast Reading.jpg'),
('Blood Glucose Meter – Beurer GL50', 'Beurer', 220.00, 150.00, '2030-12-31', 'CONTOUR blood glucose test strips box with meter and Caremed lancet set.jpg'),
('Blood Glucose Meter – Omron HGM', 'Omron', 260.00, 185.00, '2030-12-31', 'Nordic portable insulin case, cools up to 12 hours to preserve the pen.jpg'),
('Blood Glucose Meter – EasyTouch', 'EasyTouch', 210.00, 140.00, '2030-12-31', 'MCPWL Insulin Travel Bag, Thermally Insulated and Portable for Diabetes Management.jpg'),
('Blood Glucose Meter – Contour Plus', 'Contour', 280.00, 200.00, '2030-12-31', 'Premium Home Care Collection.jpg');
INSERT INTO Product
(product_name, brand, unit_price_sell, unit_price_cost, expiry_date, image)
VALUES
(
  'Pregnancy Test Strip',
  'AccuSure',
  25.00,
  10.00,
  '2027-12-31',
  'AccuFast Pregnancy Test Cassette C30C.jpg'
);
INSERT INTO Product
(product_name, brand, unit_price_sell, unit_price_cost, expiry_date, image)
VALUES
('5 Liter Pure & Clean Distilled Water, 100% Purity, for Medical and Industrial Use', 'MedClean', 15.00, 6.00, '2027-06-30', '5 Liter Pure & Clean Distilled Water, 100% Purity, for Medical and Industrial Use.jpg'),
('Med One Antibacterial 2% Antiseptic Hand Soap Solution, 1 Liter', 'PureSafe', 10.00, 4.00, '2026-12-31', 'Med One Antibacterial 2% Antiseptic Hand Soap Solution, 1 Liter.jpg'),
('Medon 10% Povidone-Iodine Antiseptic Solution, 4-Liter Bottle, Approved for Medical Use', 'CleanLab', 18.00, 8.00, '2027-03-15', 'Medon 10% Povidone-Iodine Antiseptic Solution, 4-Liter Bottle, Approved for Medical Use.jpg'),
('PureMed 75% Alcohol Sterile Medical Swabs, 100 Individually Wrapped', 'SterilPro', 22.00, 10.00, '2026-09-01', 'PureMed 75% Alcohol Sterile Medical Swabs, 100 Individually Wrapped.jpg'),
('Pure & Clean Kiss Instant Hand Sanitizer 1 Liter  Personal Sanitizer for Protection and Hygiene','SterilPro', 30.00 , 12.00 , '2026-9-29','Pure & Clean Kiss Instant Hand Sanitizer 1 Liter  Personal Sanitizer for Protection and Hygiene.jpg');


-- =========================
-- Supplier
-- =========================
CREATE TABLE Supplier (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    country VARCHAR(50)
);

INSERT INTO Supplier (supplier_name, phone, country) VALUES
('Global Lab Supplies', '0097259123456', 'Germany'),
('Scientific Equip Co', '0097259765432', 'USA');

-- =========================
-- Employee
-- =========================
CREATE TABLE Employee (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(50),
    salary DECIMAL(10,2),
    branch_id INT NOT NULL,
    warehouse_id INT,
    FOREIGN KEY (branch_id) REFERENCES Branch(branch_id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);

INSERT INTO Employee (name, position, salary, branch_id, warehouse_id) VALUES
('Ahmad Saleh', 'Warehouse Manager', 3500.00, 1, 1),
('Lina Hassan', 'Sales Employee', 2800.00, 1, NULL),
('Omar Khaled', 'Warehouse Staff', 2600.00, 2, 3);

-- =========================
-- Warehouse Stock
-- =========================
CREATE TABLE WarehouseStock (
    warehouse_id INT,
    product_id INT,
    quantity_available INT NOT NULL,
    last_restock_date DATE,
    PRIMARY KEY (warehouse_id, product_id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

INSERT INTO WarehouseStock VALUES
(1,1,15,'2025-05-01'),
(1,2,100,'2025-05-02'),
(2,2,60,'2025-05-03'),
(3,1,5,'2025-05-04'),
(3,3,40,'2025-05-05');

INSERT INTO WarehouseStock VALUES
(4, 15, 50, '2026-01-01'),
(4, 14, 40, '2025-01-017'),
(4, 13, 35, '2025-08-06'),
(4, 12, 45, '2025-01-01'),
(4, 11, 30, '2025-01-01'),
(4, 10, 60, '2025-01-01'),
(4, 9, 55, '2025-01-01');
INSERT INTO WarehouseStock VALUES
(5, 16, 100, '2025-9-5');
INSERT INTO WarehouseStock VALUES
(5, 17, 100, '2025-9-5');
INSERT INTO WarehouseStock
(warehouse_id, product_id, quantity_available, last_restock_date)
VALUES
(8, 18, 200, '2025-07-09'),
(8, 19, 300, '2025-08-23'),
(8, 20, 150, '2025-12-12'),
(8, 21, 180, '2025-01-01'),
(8, 22, 180, '2025-5-3');
-- =========================
-- Purchase Order
-- =========================
CREATE TABLE PurchaseOrder (
    po_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    total_cost DECIMAL(10,2),
    order_date DATE NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);

CREATE TABLE PurchaseOrderItem (
    po_id INT,
    product_id INT,
    warehouse_id INT,
    qty_received INT NOT NULL,
    cost_per_unit DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (po_id, product_id),
    FOREIGN KEY (po_id) REFERENCES PurchaseOrder(po_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);

INSERT INTO PurchaseOrder (supplier_id, total_cost, order_date) VALUES
(1,1200,'2025-05-06'),
(2,300,'2025-05-10');

INSERT INTO PurchaseOrderItem VALUES
(1,1,1,2,950),
(1,2,2,50,15),
(2,3,3,30,7);

-- =========================
-- Sales Order
-- =========================
CREATE TABLE SalesOrder (
    so_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    branch_id INT NOT NULL,
    sales_date DATE NOT NULL,
    total_amount DECIMAL(10,2),
    payment_status VARCHAR(30),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (branch_id) REFERENCES Branch(branch_id)
);

CREATE TABLE SalesOrderItem (
    so_id INT,
    product_id INT,
    qty_sold INT NOT NULL,
    selling_price_per_unit DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (so_id, product_id),
    FOREIGN KEY (so_id) REFERENCES SalesOrder(so_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

INSERT INTO SalesOrder (customer_id, branch_id, sales_date, total_amount, payment_status) VALUES
(1,1,'2025-05-12',2400,'Paid'),
(2,2,'2025-05-14',85,'Pending');

INSERT INTO SalesOrderItem VALUES
(1,1,2,1200),
(2,2,1,25),
(2,3,5,12);
INSERT INTO branch (city, address, phone)
VALUES ('Hebron', 'Main Street', '0591111111');
SELECT * FROM Supplier;
SELECT * FROM branch;
SELECT * FROM product;
SHOW CREATE TABLE warehousestock;
ALTER TABLE warehousestock
DROP FOREIGN KEY warehousestock_ibfk_1;
ALTER TABLE warehousestock
ADD CONSTRAINT warehousestock_ibfk_1
FOREIGN KEY (warehouse_id)
REFERENCES warehouse(warehouse_id)
ON DELETE CASCADE;
CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

INSERT INTO admin (full_name, email, password)
VALUES
('Donia Said', 'donia.admin@labmart.com', 'admin123'),
('Israa Trukman', 'Israa.admin@labmart.com', 'admin123');

SHOW TABLES;
DESCRIBE Product;
ALTER TABLE Product
DROP COLUMN category;

DESCRIBE Warehouse;
SELECT warehouse_id, warehouse_name FROM Warehouse;

INSERT INTO Product
(product_name, brand, unit_price_sell, unit_price_cost, expiry_date, image)
VALUES
('Bendex ME7517 Medical Oxygen Regulator, Adjustable Flow 0LPM', 'BreatheWell', 120.00, 65.00, '2028-12-31', 'Bendex ME7517 Medical Oxygen Regulator, Adjustable Flow 0LPM.jpg'),
('Comfortable, adjustable, soft nebulizer mask for easy breathing and medication delivery', 'MedAir', 150.00, 85.00, '2028-12-31', 'Comfortable, adjustable, soft nebulizer mask for easy breathing and medication delivery.jpg'),
('Norditalia Migan Plus NRT steam generator, piston compressor, continuous operating time', 'PureBreath', 90.00, 45.00, '2027-06-30', 'Norditalia Migan Plus NRT steam generator, piston compressor, continuous operating time.jpg'),
('Omron Comb Air Steam Inhaler', 'KidCare', 110.00, 55.00, '2027-12-31', 'Omron Comb Air Steam Inhaler.jpg'),
('Philips EverFlo home oxygen generator stable operation, easy maintenance, and reliable ', 'HealthSteam', 200.00, 120.00, '2029-01-01', 'Philips EverFlo home oxygen generator stable operation, easy maintenance, and reliable .jpg'),
('Uwell 8L Pure Oxygen Generator for Home Use', 'AirEase', 95.00, 50.00, '2028-03-15', 'Uwell 8L Pure Oxygen Generator for Home Use.jpg');

INSERT INTO WarehouseStock
(warehouse_id, product_id, quantity_available, last_restock_date)
VALUES
(10, 23, 120, '2025-01-01'),
(10, 24, 100, '2025-01-01'),
(10, 25, 140, '2025-01-01'),
(10, 26, 130, '2025-01-01'),
(10, 27, 80,  '2025-01-01'),
(10, 28, 160, '2025-01-01');


