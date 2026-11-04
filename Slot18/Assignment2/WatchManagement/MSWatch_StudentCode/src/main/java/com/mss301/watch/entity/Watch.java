package com.mss301.watch.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;

// [TODO-6.16: entity Watches (BrandID chỉ là tham chiếu, không join)]
@Entity
@Table(name = "Watches")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Watch {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "WatchID")
    private Integer watchId;

    @Column(name = "Name", nullable = false, length = 255)
    private String name;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "CategoryID")
    private WatchCategory category;

    @Column(name = "BrandID")
    private Integer brandId; // Reference only, no join (Database per Service)

    @Column(name = "CaseMaterial", length = 100)
    private String caseMaterial;

    @Column(name = "StrapMaterial", length = 100)
    private String strapMaterial;

    @Column(name = "WaterpMaterial", length = 50)
    private String waterpMaterial;

    @Column(name = "Price", precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "ReleaseDate")
    private LocalDate releaseDate;

    @Column(name = "Stock")
    private Integer stock;
}
