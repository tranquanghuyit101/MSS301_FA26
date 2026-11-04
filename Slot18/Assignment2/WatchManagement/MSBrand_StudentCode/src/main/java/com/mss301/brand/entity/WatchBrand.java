package com.mss301.brand.entity;

import jakarta.persistence.*;
import lombok.*;

// [TODO-5.1: entity WatchBrand]
@Entity
@Table(name = "WatchBrands")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WatchBrand {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "BrandID")
    private Integer brandId;

    @Column(name = "BrandName", nullable = false, length = 100)
    private String brandName;

    @Column(name = "CountryOfOrigin", length = 100)
    private String countryOfOrigin;
}
