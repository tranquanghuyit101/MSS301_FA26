package com.mss301.watch;

import com.mss301.watch.entity.Watch;
import com.mss301.watch.entity.WatchCategory;
import com.mss301.watch.repository.WatchCategoryRepository;
import com.mss301.watch.repository.WatchRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

/** Seed đúng dữ liệu trong đề bài (mục 2 - Data). */
// [TODO-6.16: seed đúng nguyên văn đề bài]
@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final WatchRepository watchRepository;
    private final WatchCategoryRepository categoryRepository;

    @Override
    public void run(String... args) {
        if (categoryRepository.count() == 0) {
            List<WatchCategory> categories = List.of(
                category("Dive Watches", "Designed for underwater diving and feature high water resistance.",
                    "Automatic", "$500 - $10,000"),
                category("Chronograph Watches", "Watches with a stopwatch function in addition to the main display.",
                    "Automatic or Quartz", "$300 - $8,000"),
                category("Dress Watches", "Elegant and simple, intended to be worn with formal wear.",
                    "Automatic or Manual", "$400 - $20,000"),
                category("Digital Watches", "Watches with an LCD or LED screen that show time in a digital format.",
                    "Quartz", "$50 - $500"),
                category("Pilot Watches", "Originally designed for aviators, featuring large, easy-to-read dials.",
                    "Automatic", "$700 - $15,000")
            );
            categoryRepository.saveAll(categories);
            log.info("Seeded {} categories", categories.size());
        }

        if (watchRepository.count() == 0) {
            List<WatchCategory> cats = categoryRepository.findAll();
            WatchCategory dive = cats.get(0), chrono = cats.get(1), dress = cats.get(2),
                          digital = cats.get(3), pilot = cats.get(4);

            // Thứ tự lưu quyết định WatchID 1..10 -> phải khớp với BrandWatches seed trong MSBrand
            List<Watch> watches = List.of(
                watch("Submariner Date", dive, 1, "Oystersteel", "Oystersteel", "300 meters", "9550.00", LocalDate.of(2020, 9, 1), 50),
                watch("Speedmaster Moonwatch Professional", chrono, 2, "Stainless Steel", "Stainless Steel", "50 meters", "7200.00", LocalDate.of(2021, 1, 5), 75),
                watch("Presage Cocktail Time", dress, 3, "Stainless Steel", "Leather", "50 meters", "425.00", LocalDate.of(2019, 6, 1), 200),
                watch("G-Shock DW-5600E-1V", digital, 4, "Resin", "Resin", "200 meters", "69.95", LocalDate.of(1996, 6, 12), 500),
                watch("Carrera Calibre Heuer 02", chrono, 5, "Stainless Steel", "Alligator Leather", "100 meters", "5900.00", LocalDate.of(2022, 3, 30), 60),
                watch("Seamaster Diver 300M", dive, 2, "Stainless Steel", "Rubber", "300 meters", "5400.00", LocalDate.of(2018, 2, 15), 120),
                watch("Prospex SPB143", dive, 3, "Stainless Steel", "Stainless Steel", "200 meters", "1200.00", LocalDate.of(2020, 7, 1), 150),
                watch("Daytona", chrono, 1, "Oystersteel", "Oystersteel", "100 meters", "14550.00", LocalDate.of(2016, 3, 16), 30),
                watch("F-91W", digital, 4, "Resin", "Resin", "30 meters", "19.99", LocalDate.of(1989, 1, 1), 1000),
                watch("IWC Pilot's Watch Mark XVIII", pilot, 4, "Stainless Steel", "Leather", "60 meters", "4500.00", LocalDate.of(2016, 1, 18), 80)
            );
            watchRepository.saveAll(watches);
            log.info("Seeded {} watches", watches.size());
        }
    }

    private WatchCategory category(String name, String description, String movement, String priceRange) {
        return WatchCategory.builder().categoryName(name).description(description)
            .movementType(movement).priceRange(priceRange).build();
    }

    private Watch watch(String name, WatchCategory category, int brandId, String caseMaterial, String strap,
                        String water, String price, LocalDate releaseDate, int stock) {
        return Watch.builder().name(name).category(category).brandId(brandId)
            .caseMaterial(caseMaterial).strapMaterial(strap).waterpMaterial(water)
            .price(new BigDecimal(price)).releaseDate(releaseDate).stock(stock).build();
    }
}
