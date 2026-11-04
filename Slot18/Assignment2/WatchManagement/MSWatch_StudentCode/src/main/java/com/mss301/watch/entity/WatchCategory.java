package com.mss301.watch.entity;

import jakarta.persistence.*;
import lombok.*;

// [TODO-6.16: entity WatchCategory]
@Entity
@Table(name = "WatchCategories")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WatchCategory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "CategoryID")
    private Integer categoryId;

    @Column(name = "CategoryName", nullable = false, length = 100)
    private String categoryName;

    @Column(name = "Description", length = 500)
    private String description;

    @Column(name = "MovementType", length = 50)
    private String movementType;

    @Column(name = "PriceRange", length = 50)
    private String priceRange;
}
