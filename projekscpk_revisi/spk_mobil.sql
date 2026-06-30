-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: May 18, 2026 at 12:48 PM
-- Server version: 8.0.30
-- PHP Version: 8.5.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `spk_mobil`
--

-- --------------------------------------------------------

--
-- Table structure for table `hasil_rekomendasi`
--

CREATE TABLE `hasil_rekomendasi` (
  `id` int NOT NULL,
  `car_name` varchar(100) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `selling_price` float DEFAULT NULL,
  `umur` int DEFAULT NULL,
  `kms_driven` int DEFAULT NULL,
  `rasio_harga` float DEFAULT NULL,
  `owner` int DEFAULT NULL,
  `fuel_type` varchar(20) DEFAULT NULL,
  `transmission` varchar(20) DEFAULT NULL,
  `skor_fuzzy` float DEFAULT NULL,
  `status_rekomendasi` varchar(30) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `hasil_rekomendasi`
--

INSERT INTO `hasil_rekomendasi` (`id`, `car_name`, `year`, `selling_price`, `umur`, `kms_driven`, `rasio_harga`, `owner`, `fuel_type`, `transmission`, `skor_fuzzy`, `status_rekomendasi`, `created_at`) VALUES
(2, 'Bajaj Pulsar 220 F', 2016, 0.51, 8, 24000, 0.54, 0, 'Petrol', 'Manual', 0.794, 'Direkomendasikan', '2026-05-16 11:43:12'),
(3, 'alto 800', 2017, 2.85, 7, 2135, 0.79, 0, 'Petrol', 'Manual', 0.768, 'Direkomendasikan', '2026-05-16 11:43:38'),
(4, 'Bajaj Pulsar 220 F', 2016, 0.51, 8, 24000, 0.54, 0, 'Petrol', 'Manual', 0.794, 'Direkomendasikan', '2026-05-16 11:48:50'),
(5, 'Hyosung GT250R', 2014, 1.35, 10, 16500, 0.39, 1, 'Petrol', 'Manual', 0.8, 'Direkomendasikan', '2026-05-16 11:55:02'),
(6, 'Honda CB Hornet 160R', 2016, 0.6, 8, 15000, 0.69, 0, 'Petrol', 'Manual', 0.776, 'Direkomendasikan', '2026-05-16 12:06:52'),
(7, 'Activa 4g', 2017, 0.4, 7, 1300, 0.78, 0, 'Petrol', 'Automatic', 0.784, 'Direkomendasikan', '2026-05-16 12:11:23'),
(8, 'Hyosung GT250R', 2014, 1.35, 10, 16500, 0.39, 1, 'Petrol', 'Manual', 0.8, 'Direkomendasikan', '2026-05-18 06:16:35');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `hasil_rekomendasi`
--
ALTER TABLE `hasil_rekomendasi`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `hasil_rekomendasi`
--
ALTER TABLE `hasil_rekomendasi`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
