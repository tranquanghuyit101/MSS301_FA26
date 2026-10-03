import os

BASE_DIR = r"d:\FA26\MSS301\Code\Assignment\fu-cinema\booking-service"
JAVA_DIR = os.path.join(BASE_DIR, r"src\main\java\com\fudn\bookingservice")
RES_DIR = os.path.join(BASE_DIR, r"src\main\resources")

# 1. Migration
v1_sql = """CREATE TABLE booking (
    booking_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    booking_date   DATETIME      NOT NULL,
    total_price    DECIMAL(12,2) NOT NULL,
    customer_id    BIGINT        NOT NULL,
    booking_status VARCHAR(20)   NOT NULL,
    INDEX idx_booking_customer (customer_id),
    INDEX idx_booking_date (booking_date)
);

CREATE TABLE booking_detail (
    booking_detail_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    booking_id        BIGINT        NOT NULL,
    showtime_id       VARCHAR(24)   NOT NULL,
    seat_code         VARCHAR(5)    NOT NULL,
    price             DECIMAL(10,2) NOT NULL,
    movie_id          VARCHAR(24)   NOT NULL,
    movie_title       VARCHAR(200)  NOT NULL,
    room_name         VARCHAR(50)   NOT NULL,
    showtime_start    DATETIME      NOT NULL,
    CONSTRAINT fk_detail_booking FOREIGN KEY (booking_id) REFERENCES booking (booking_id),
    INDEX idx_detail_showtime_seat (showtime_id, seat_code)
);
"""

mig_dir = os.path.join(RES_DIR, r"db\migration")
os.makedirs(mig_dir, exist_ok=True)
with open(os.path.join(mig_dir, "V1__init.sql"), "w", encoding="utf-8") as f:
    f.write(v1_sql)
print("Created V1__init.sql")

files = {
    "model/BookingStatus.java": """package com.fudn.bookingservice.model;
public enum BookingStatus { CONFIRMED, CANCELLED }
""",
    "model/Booking.java": """package com.fudn.bookingservice.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "booking")
@Getter
@Setter
@NoArgsConstructor
public class Booking {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long bookingId;

    @Column(nullable = false)
    private LocalDateTime bookingDate;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal totalPrice;

    @Column(nullable = false)
    private Long customerId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private BookingStatus bookingStatus;

    @OneToMany(mappedBy = "booking", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("bookingDetailId ASC")
    private List<BookingDetail> details = new ArrayList<>();

    public void addDetail(BookingDetail detail) {
        details.add(detail);
        detail.setBooking(this);
    }
}
""",
    "model/BookingDetail.java": """package com.fudn.bookingservice.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "booking_detail")
@Getter
@Setter
@NoArgsConstructor
public class BookingDetail {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long bookingDetailId;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "booking_id", nullable = false)
    private Booking booking;

    @Column(nullable = false, length = 24)
    private String showtimeId;

    @Column(nullable = false, length = 5)
    private String seatCode;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(nullable = false, length = 24)
    private String movieId;

    @Column(nullable = false, length = 200)
    private String movieTitle;

    @Column(nullable = false, length = 50)
    private String roomName;

    @Column(nullable = false)
    private LocalDateTime showtimeStart;
}
""",
    "repository/BookingRepository.java": """package com.fudn.bookingservice.repository;

import com.fudn.bookingservice.model.Booking;
import com.fudn.bookingservice.model.BookingStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface BookingRepository extends JpaRepository<Booking, Long> {

    List<Booking> findByCustomerIdOrderByBookingDateDesc(Long customerId);

    List<Booking> findAllByOrderByBookingDateDesc();

    @Query(\"\"\"
            select b from Booking b
            where b.bookingStatus = :status
              and b.bookingDate >= :from
              and b.bookingDate < :to
            order by b.bookingDate desc
            \"\"\")
    List<Booking> findForReport(@Param("status") BookingStatus status,
                                @Param("from") LocalDateTime from,
                                @Param("to") LocalDateTime to);
}
""",
    "repository/BookingDetailRepository.java": """package com.fudn.bookingservice.repository;

import com.fudn.bookingservice.model.BookingDetail;
import com.fudn.bookingservice.model.BookingStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface BookingDetailRepository extends JpaRepository<BookingDetail, Long> {

    @Query(\"\"\"
            select d.seatCode from BookingDetail d
            where d.showtimeId = :showtimeId
              and d.booking.bookingStatus = :status
            \"\"\")
    List<String> findSeatCodesByShowtime(@Param("showtimeId") String showtimeId,
                                         @Param("status") BookingStatus status);
}
""",
    "dto/ShowtimeResponse.java": """package com.fudn.bookingservice.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ShowtimeResponse(String showtimeId, String movieId, String movieTitle,
                               String roomId, String roomName, int seatRows, int seatsPerRow,
                               LocalDateTime startTime, LocalDateTime endTime,
                               BigDecimal ticketPrice, String showtimeStatus) {
}
""",
    "client/MovieClient.java": """package com.fudn.bookingservice.client;

import com.fudn.bookingservice.dto.ShowtimeResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@FeignClient(value = "movie-service", url = "${movie.service.url}")
public interface MovieClient {

    @GetMapping("/api/showtimes/{id}")
    ShowtimeResponse getShowtime(@PathVariable("id") String id);
}
""",
    "dto/BookingItemRequest.java": """package com.fudn.bookingservice.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public record BookingItemRequest(
        @NotBlank(message = "Showtime id is required") String showtimeId,
        @NotBlank(message = "Seat code is required")
        @Pattern(regexp = "^[A-Z][1-9][0-9]?$", message = "Seat code must look like A1, E10 ...") String seatCode) {
}
""",
    "dto/CreateBookingRequest.java": """package com.fudn.bookingservice.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;

import java.util.List;

public record CreateBookingRequest(
        @NotEmpty(message = "Booking must have at least 1 ticket")
        @Size(max = 8, message = "A booking can have at most 8 tickets")
        List<@Valid BookingItemRequest> items) {
}
""",
    "dto/BookingDetailResponse.java": """package com.fudn.bookingservice.dto;

import com.fudn.bookingservice.model.BookingDetail;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record BookingDetailResponse(String showtimeId, String movieId, String movieTitle, String roomName,
                                    LocalDateTime showtimeStart, String seatCode, BigDecimal price) {
    public static BookingDetailResponse from(BookingDetail d) {
        return new BookingDetailResponse(d.getShowtimeId(), d.getMovieId(), d.getMovieTitle(), d.getRoomName(),
                d.getShowtimeStart(), d.getSeatCode(), d.getPrice());
    }
}
""",
    "dto/BookingResponse.java": """package com.fudn.bookingservice.dto;

import com.fudn.bookingservice.model.Booking;
import com.fudn.bookingservice.model.BookingStatus;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public record BookingResponse(Long bookingId, LocalDateTime bookingDate, Long customerId,
                              BigDecimal totalPrice, BookingStatus bookingStatus,
                              List<BookingDetailResponse> details) {
    public static BookingResponse from(Booking b) {
        return new BookingResponse(b.getBookingId(), b.getBookingDate(), b.getCustomerId(),
                b.getTotalPrice(), b.getBookingStatus(),
                b.getDetails().stream().map(BookingDetailResponse::from).toList());
    }
}
""",
    "dto/SeatMapResponse.java": """package com.fudn.bookingservice.dto;

import java.time.LocalDateTime;
import java.util.List;

public record SeatMapResponse(String showtimeId, String movieTitle, String roomName, LocalDateTime startTime,
                              int seatRows, int seatsPerRow, int totalSeats, int availableSeats,
                              List<String> bookedSeats) {
}
""",
    "dto/MovieRevenueResponse.java": """package com.fudn.bookingservice.dto;

import java.math.BigDecimal;

public record MovieRevenueResponse(String movieId, String movieTitle, long ticketsSold, BigDecimal revenue) {
}
""",
    "dto/ReportResponse.java": """package com.fudn.bookingservice.dto;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public record ReportResponse(LocalDate startDate, LocalDate endDate,
                             long totalBookings, long totalTickets, BigDecimal totalRevenue,
                             List<MovieRevenueResponse> revenueByMovie,
                             List<BookingResponse> bookings) {
}
""",
    "service/BookingService.java": """package com.fudn.bookingservice.service;

import com.fudn.bookingservice.client.MovieClient;
import com.fudn.bookingservice.dto.*;
import com.fudn.bookingservice.exception.ApiException;
import com.fudn.bookingservice.model.Booking;
import com.fudn.bookingservice.model.BookingDetail;
import com.fudn.bookingservice.model.BookingStatus;
import com.fudn.bookingservice.repository.BookingDetailRepository;
import com.fudn.bookingservice.repository.BookingRepository;
import feign.FeignException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class BookingService {

    public static final String ROLE_ADMIN = "ADMIN";
    private static final int CANCEL_BEFORE_HOURS = 2;

    private final BookingRepository bookingRepository;
    private final BookingDetailRepository bookingDetailRepository;
    private final MovieClient movieClient;

    public SeatMapResponse getSeatMap(String showtimeId) {
        ShowtimeResponse st = fetchShowtime(showtimeId);
        List<String> booked = bookingDetailRepository
                .findSeatCodesByShowtime(showtimeId, BookingStatus.CONFIRMED)
                .stream().sorted().toList();
        int totalSeats = st.seatRows() * st.seatsPerRow();
        return new SeatMapResponse(st.showtimeId(), st.movieTitle(), st.roomName(), st.startTime(),
                st.seatRows(), st.seatsPerRow(), totalSeats, totalSeats - booked.size(), booked);
    }

    @Transactional
    public BookingResponse create(Long customerId, CreateBookingRequest request) {
        Map<String, ShowtimeResponse> showtimeCache = new HashMap<>();
        Map<String, Set<String>> bookedSeatCache = new HashMap<>();
        Set<String> requestedSeats = new HashSet<>();

        Booking booking = new Booking();
        booking.setCustomerId(customerId);
        booking.setBookingDate(LocalDateTime.now());
        booking.setBookingStatus(BookingStatus.CONFIRMED);
        BigDecimal total = BigDecimal.ZERO;

        for (BookingItemRequest item : request.items()) {
            String seat = item.seatCode();

            if (!requestedSeats.add(item.showtimeId() + "#" + seat)) {
                throw ApiException.badRequest("Duplicate seat " + seat + " of showtime " + item.showtimeId() + " in request");
            }

            ShowtimeResponse st = showtimeCache.computeIfAbsent(item.showtimeId(), this::fetchShowtime);
            validateShowtime(st);
            validateSeat(seat, st);

            Set<String> taken = bookedSeatCache.computeIfAbsent(st.showtimeId(),
                    id -> new HashSet<>(bookingDetailRepository.findSeatCodesByShowtime(id, BookingStatus.CONFIRMED)));
            if (taken.contains(seat)) {
                throw ApiException.conflict("Seat " + seat + " of showtime " + st.showtimeId() + " is already booked");
            }

            BookingDetail detail = new BookingDetail();
            detail.setShowtimeId(st.showtimeId());
            detail.setSeatCode(seat);
            detail.setPrice(st.ticketPrice());
            detail.setMovieId(st.movieId());
            detail.setMovieTitle(st.movieTitle());
            detail.setRoomName(st.roomName());
            detail.setShowtimeStart(st.startTime());
            booking.addDetail(detail);

            total = total.add(st.ticketPrice());
        }

        booking.setTotalPrice(total);
        Booking saved = bookingRepository.save(booking);
        log.info("Booking {} created for customer {} with {} ticket(s), total {}",
                saved.getBookingId(), customerId, saved.getDetails().size(), total);
        return BookingResponse.from(saved);
    }

    public List<BookingResponse> getMyBookings(Long customerId) {
        return bookingRepository.findByCustomerIdOrderByBookingDateDesc(customerId)
                .stream().map(BookingResponse::from).toList();
    }

    public List<BookingResponse> getAll() {
        return bookingRepository.findAllByOrderByBookingDateDesc()
                .stream().map(BookingResponse::from).toList();
    }

    public BookingResponse getById(Long bookingId, Long userId, String role) {
        return BookingResponse.from(findAccessible(bookingId, userId, role));
    }

    @Transactional
    public BookingResponse cancel(Long bookingId, Long userId, String role) {
        Booking booking = findAccessible(bookingId, userId, role);
        if (booking.getBookingStatus() != BookingStatus.CONFIRMED) {
            throw ApiException.badRequest("Only CONFIRMED bookings can be cancelled");
        }
        if (!ROLE_ADMIN.equals(role)) {
            LocalDateTime deadline = LocalDateTime.now().plusHours(CANCEL_BEFORE_HOURS);
            boolean tooLate = booking.getDetails().stream()
                    .anyMatch(d -> d.getShowtimeStart().isBefore(deadline));
            if (tooLate) {
                throw ApiException.badRequest("Booking can only be cancelled at least "
                        + CANCEL_BEFORE_HOURS + " hours before the showtime");
            }
        }
        booking.setBookingStatus(BookingStatus.CANCELLED);
        return BookingResponse.from(bookingRepository.save(booking));
    }

    public ReportResponse report(LocalDate startDate, LocalDate endDate) {
        if (startDate.isAfter(endDate)) {
            throw ApiException.badRequest("startDate must be before or equal to endDate");
        }
        List<Booking> bookings = bookingRepository.findForReport(BookingStatus.CONFIRMED,
                startDate.atStartOfDay(), endDate.plusDays(1).atStartOfDay());

        BigDecimal totalRevenue = BigDecimal.ZERO;
        long totalTickets = 0;
        Map<String, MovieRevenueResponse> byMovie = new HashMap<>();

        for (Booking b : bookings) {
            totalRevenue = totalRevenue.add(b.getTotalPrice());
            totalTickets += b.getDetails().size();
            for (BookingDetail d : b.getDetails()) {
                byMovie.merge(d.getMovieId(),
                        new MovieRevenueResponse(d.getMovieId(), d.getMovieTitle(), 1, d.getPrice()),
                        (a, c) -> new MovieRevenueResponse(a.movieId(), a.movieTitle(),
                                a.ticketsSold() + c.ticketsSold(), a.revenue().add(c.revenue())));
            }
        }

        List<MovieRevenueResponse> revenueByMovie = byMovie.values().stream()
                .sorted(Comparator.comparing(MovieRevenueResponse::revenue).reversed()
                        .thenComparing(Comparator.comparingLong(MovieRevenueResponse::ticketsSold).reversed()))
                .toList();

        return new ReportResponse(startDate, endDate, bookings.size(), totalTickets, totalRevenue,
                revenueByMovie, bookings.stream().map(BookingResponse::from).toList());
    }

    private ShowtimeResponse fetchShowtime(String showtimeId) {
        try {
            return movieClient.getShowtime(showtimeId);
        } catch (FeignException.NotFound e) {
            throw ApiException.notFound("Showtime not found with id: " + showtimeId);
        } catch (FeignException e) {
            log.error("Cannot call movie-service: {}", e.getMessage());
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "Movie service is unavailable. Please try again later.");
        }
    }

    private void validateShowtime(ShowtimeResponse st) {
        if (!"SCHEDULED".equals(st.showtimeStatus())) {
            throw ApiException.badRequest("Showtime " + st.showtimeId() + " is not available (" + st.showtimeStatus() + ")");
        }
        if (!st.startTime().isAfter(LocalDateTime.now())) {
            throw ApiException.badRequest("Showtime " + st.showtimeId() + " has already started");
        }
    }

    private void validateSeat(String seat, ShowtimeResponse st) {
        int rowIndex = seat.charAt(0) - 'A';
        int number = Integer.parseInt(seat.substring(1));
        if (rowIndex >= st.seatRows() || number > st.seatsPerRow()) {
            char lastRow = (char) ('A' + st.seatRows() - 1);
            throw ApiException.badRequest("Seat " + seat + " does not exist in room " + st.roomName()
                    + " (rows A-" + lastRow + ", seats 1-" + st.seatsPerRow() + ")");
        }
    }

    private Booking findAccessible(Long bookingId, Long userId, String role) {
        Booking booking = bookingRepository.findById(bookingId)
                .orElseThrow(() -> ApiException.notFound("Booking not found with id: " + bookingId));
        if (!ROLE_ADMIN.equals(role) && !booking.getCustomerId().equals(userId)) {
            throw ApiException.forbidden("You can only access your own bookings");
        }
        return booking;
    }
}
""",
    "controller/BookingController.java": """package com.fudn.bookingservice.controller;

import com.fudn.bookingservice.dto.BookingResponse;
import com.fudn.bookingservice.dto.CreateBookingRequest;
import com.fudn.bookingservice.dto.ReportResponse;
import com.fudn.bookingservice.dto.SeatMapResponse;
import com.fudn.bookingservice.service.BookingService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/bookings")
@RequiredArgsConstructor
public class BookingController {

    private static final String USER_ID = "X-User-Id";
    private static final String USER_ROLE = "X-User-Role";

    private final BookingService bookingService;

    @GetMapping("/showtimes/{showtimeId}/seats")
    public SeatMapResponse getSeatMap(@PathVariable String showtimeId) {
        return bookingService.getSeatMap(showtimeId);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public BookingResponse create(@RequestHeader(USER_ID) Long userId,
                                  @Valid @RequestBody CreateBookingRequest request) {
        return bookingService.create(userId, request);
    }

    @GetMapping("/my")
    public List<BookingResponse> getMyBookings(@RequestHeader(USER_ID) Long userId) {
        return bookingService.getMyBookings(userId);
    }

    @GetMapping
    public List<BookingResponse> getAll() {
        return bookingService.getAll();
    }

    @GetMapping("/report")
    public ReportResponse report(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        return bookingService.report(startDate, endDate);
    }

    @GetMapping("/{id}")
    public BookingResponse getById(@PathVariable Long id,
                                   @RequestHeader(USER_ID) Long userId,
                                   @RequestHeader(value = USER_ROLE, required = false) String role) {
        return bookingService.getById(id, userId, role);
    }

    @PutMapping("/{id}/cancel")
    public BookingResponse cancel(@PathVariable Long id,
                                  @RequestHeader(USER_ID) Long userId,
                                  @RequestHeader(value = USER_ROLE, required = false) String role) {
        return bookingService.cancel(id, userId, role);
    }
}
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(JAVA_DIR, rel_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {rel_path}")

print("All booking-service files created successfully!")
