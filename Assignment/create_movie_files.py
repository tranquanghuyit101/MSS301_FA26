import os

BASE_DIR = r"d:\FA26\MSS301\Code\Assignment\fu-cinema\movie-service\src\main\java\com\fudn\movieservice"

files = {
    "model/RoomType.java": """package com.fudn.movieservice.model;
public enum RoomType { STANDARD, THREE_D, IMAX }
""",
    "model/RoomStatus.java": """package com.fudn.movieservice.model;
public enum RoomStatus { ACTIVE, MAINTENANCE }
""",
    "model/AgeRating.java": """package com.fudn.movieservice.model;
public enum AgeRating { P, T13, T16, T18 }
""",
    "model/MovieStatus.java": """package com.fudn.movieservice.model;
public enum MovieStatus { COMING_SOON, NOW_SHOWING, ENDED }
""",
    "model/ShowtimeStatus.java": """package com.fudn.movieservice.model;
public enum ShowtimeStatus { SCHEDULED, CANCELLED }
""",
    "model/Genre.java": """package com.fudn.movieservice.model;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "genres")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Genre {

    @Id
    private String genreId;

    @Indexed(unique = true)
    private String genreName;

    private String description;
}
""",
    "model/CinemaRoom.java": """package com.fudn.movieservice.model;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "cinema_rooms")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class CinemaRoom {

    @Id
    private String roomId;

    @Indexed(unique = true)
    private String roomName;

    private RoomType roomType;
    private Integer seatRows;
    private Integer seatsPerRow;
    private RoomStatus roomStatus;

    public int getTotalSeats() {
        return (seatRows != null && seatsPerRow != null) ? seatRows * seatsPerRow : 0;
    }
}
""",
    "model/Movie.java": """package com.fudn.movieservice.model;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDate;

@Document(collection = "movies")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Movie {

    @Id
    private String movieId;

    private String title;
    private String description;
    private String director;
    private Integer durationMinutes;
    private String language;
    private AgeRating ageRating;
    private LocalDate releaseDate;

    @Indexed
    private String genreId;

    private MovieStatus movieStatus;
}
""",
    "model/Showtime.java": """package com.fudn.movieservice.model;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.CompoundIndex;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;
import org.springframework.data.mongodb.core.mapping.FieldType;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Document(collection = "showtimes")
@CompoundIndex(name = "room_start_idx", def = "{'roomId': 1, 'startTime': 1}")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Showtime {

    @Id
    private String showtimeId;

    @Indexed
    private String movieId;

    private String roomId;

    private LocalDateTime startTime;
    private LocalDateTime endTime;

    @Field(targetType = FieldType.DECIMAL128)
    private BigDecimal ticketPrice;

    private ShowtimeStatus showtimeStatus;
}
""",
    "repository/GenreRepository.java": """package com.fudn.movieservice.repository;

import com.fudn.movieservice.model.Genre;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface GenreRepository extends MongoRepository<Genre, String> {
    boolean existsByGenreNameIgnoreCase(String genreName);
    boolean existsByGenreNameIgnoreCaseAndGenreIdNot(String genreName, String genreId);
}
""",
    "repository/RoomRepository.java": """package com.fudn.movieservice.repository;

import com.fudn.movieservice.model.CinemaRoom;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface RoomRepository extends MongoRepository<CinemaRoom, String> {
    boolean existsByRoomNameIgnoreCase(String roomName);
    boolean existsByRoomNameIgnoreCaseAndRoomIdNot(String roomName, String roomId);
}
""",
    "repository/MovieRepository.java": """package com.fudn.movieservice.repository;

import com.fudn.movieservice.model.Movie;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface MovieRepository extends MongoRepository<Movie, String> {
    boolean existsByGenreId(String genreId);
}
""",
    "repository/ShowtimeRepository.java": """package com.fudn.movieservice.repository;

import com.fudn.movieservice.model.Showtime;
import com.fudn.movieservice.model.ShowtimeStatus;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.time.LocalDateTime;
import java.util.List;

public interface ShowtimeRepository extends MongoRepository<Showtime, String> {

    boolean existsByRoomId(String roomId);

    boolean existsByMovieId(String movieId);

    List<Showtime> findAllByOrderByStartTimeAsc();

    List<Showtime> findByMovieIdOrderByStartTimeAsc(String movieId);

    long countByRoomIdAndShowtimeStatusAndStartTimeLessThanAndEndTimeGreaterThanAndShowtimeIdNot(
            String roomId, ShowtimeStatus status, LocalDateTime newEndTime, LocalDateTime newStartTime,
            String excludeShowtimeId);
}
""",
    "dto/GenreRequest.java": """package com.fudn.movieservice.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record GenreRequest(
        @NotBlank(message = "Genre name is required") @Size(max = 50) String genreName,
        @Size(max = 255) String description) {
}
""",
    "dto/GenreResponse.java": """package com.fudn.movieservice.dto;

import com.fudn.movieservice.model.Genre;

public record GenreResponse(String genreId, String genreName, String description) {
    public static GenreResponse from(Genre g) {
        return new GenreResponse(g.getGenreId(), g.getGenreName(), g.getDescription());
    }
}
""",
    "dto/RoomRequest.java": """package com.fudn.movieservice.dto;

import com.fudn.movieservice.model.RoomStatus;
import com.fudn.movieservice.model.RoomType;
import jakarta.validation.constraints.*;

public record RoomRequest(
        @NotBlank(message = "Room name is required") @Size(max = 50) String roomName,
        @NotNull(message = "Room type is required") RoomType roomType,
        @NotNull @Min(value = 1, message = "seatRows must be 1-26") @Max(value = 26, message = "seatRows must be 1-26") Integer seatRows,
        @NotNull @Min(value = 1, message = "seatsPerRow must be 1-30") @Max(value = 30, message = "seatsPerRow must be 1-30") Integer seatsPerRow,
        @NotNull(message = "Room status is required") RoomStatus roomStatus) {
}
""",
    "dto/RoomResponse.java": """package com.fudn.movieservice.dto;

import com.fudn.movieservice.model.CinemaRoom;
import com.fudn.movieservice.model.RoomStatus;
import com.fudn.movieservice.model.RoomType;

public record RoomResponse(String roomId, String roomName, RoomType roomType,
                           int seatRows, int seatsPerRow, int totalSeats, RoomStatus roomStatus) {
    public static RoomResponse from(CinemaRoom r) {
        return new RoomResponse(r.getRoomId(), r.getRoomName(), r.getRoomType(),
                r.getSeatRows(), r.getSeatsPerRow(), r.getTotalSeats(), r.getRoomStatus());
    }
}
""",
    "dto/MovieRequest.java": """package com.fudn.movieservice.dto;

import com.fudn.movieservice.model.AgeRating;
import com.fudn.movieservice.model.MovieStatus;
import jakarta.validation.constraints.*;

import java.time.LocalDate;

public record MovieRequest(
        @NotBlank(message = "Title is required") @Size(max = 200) String title,
        @Size(max = 2000) String description,
        @Size(max = 100) String director,
        @NotNull(message = "Duration is required")
        @Min(value = 30, message = "Duration must be 30-300 minutes")
        @Max(value = 300, message = "Duration must be 30-300 minutes") Integer durationMinutes,
        @Size(max = 50) String language,
        @NotNull(message = "Age rating is required") AgeRating ageRating,
        LocalDate releaseDate,
        @NotBlank(message = "Genre id is required") String genreId,
        @NotNull(message = "Movie status is required") MovieStatus movieStatus) {
}
""",
    "dto/MovieResponse.java": """package com.fudn.movieservice.dto;

import com.fudn.movieservice.model.AgeRating;
import com.fudn.movieservice.model.Movie;
import com.fudn.movieservice.model.MovieStatus;

import java.time.LocalDate;

public record MovieResponse(String movieId, String title, String description, String director,
                            Integer durationMinutes, String language, AgeRating ageRating,
                            LocalDate releaseDate, String genreId, String genreName, MovieStatus movieStatus) {
    public static MovieResponse from(Movie m, String genreName) {
        return new MovieResponse(m.getMovieId(), m.getTitle(), m.getDescription(), m.getDirector(),
                m.getDurationMinutes(), m.getLanguage(), m.getAgeRating(), m.getReleaseDate(),
                m.getGenreId(), genreName, m.getMovieStatus());
    }
}
""",
    "dto/ShowtimeRequest.java": """package com.fudn.movieservice.dto;

import jakarta.validation.constraints.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ShowtimeRequest(
        @NotBlank(message = "Movie id is required") String movieId,
        @NotBlank(message = "Room id is required") String roomId,
        @NotNull(message = "Start time is required")
        @Future(message = "Start time must be in the future") LocalDateTime startTime,
        @NotNull(message = "Ticket price is required")
        @DecimalMin(value = "10000", message = "Ticket price must be at least 10,000")
        @DecimalMax(value = "1000000", message = "Ticket price must not exceed 1,000,000") BigDecimal ticketPrice) {
}
""",
    "dto/ShowtimeResponse.java": """package com.fudn.movieservice.dto;

import com.fudn.movieservice.model.CinemaRoom;
import com.fudn.movieservice.model.Movie;
import com.fudn.movieservice.model.Showtime;
import com.fudn.movieservice.model.ShowtimeStatus;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ShowtimeResponse(String showtimeId, String movieId, String movieTitle,
                               String roomId, String roomName, int seatRows, int seatsPerRow,
                               LocalDateTime startTime, LocalDateTime endTime,
                               BigDecimal ticketPrice, ShowtimeStatus showtimeStatus) {
    public static ShowtimeResponse from(Showtime s, Movie movie, CinemaRoom room) {
        return new ShowtimeResponse(s.getShowtimeId(),
                movie.getMovieId(), movie.getTitle(),
                room.getRoomId(), room.getRoomName(), room.getSeatRows(), room.getSeatsPerRow(),
                s.getStartTime(), s.getEndTime(), s.getTicketPrice(), s.getShowtimeStatus());
    }
}
""",
    "service/GenreService.java": """package com.fudn.movieservice.service;

import com.fudn.movieservice.dto.GenreRequest;
import com.fudn.movieservice.dto.GenreResponse;
import com.fudn.movieservice.exception.ApiException;
import com.fudn.movieservice.model.Genre;
import com.fudn.movieservice.repository.GenreRepository;
import com.fudn.movieservice.repository.MovieRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class GenreService {

    private final GenreRepository genreRepository;
    private final MovieRepository movieRepository;

    public List<GenreResponse> getAll() {
        return genreRepository.findAll(Sort.by("genreName")).stream().map(GenreResponse::from).toList();
    }

    public GenreResponse getById(String id) {
        return GenreResponse.from(find(id));
    }

    public GenreResponse create(GenreRequest request) {
        if (genreRepository.existsByGenreNameIgnoreCase(request.genreName())) {
            throw ApiException.conflict("Genre name already exists: " + request.genreName());
        }
        Genre genre = new Genre();
        genre.setGenreName(request.genreName());
        genre.setDescription(request.description());
        return GenreResponse.from(genreRepository.save(genre));
    }

    public GenreResponse update(String id, GenreRequest request) {
        Genre genre = find(id);
        if (genreRepository.existsByGenreNameIgnoreCaseAndGenreIdNot(request.genreName(), id)) {
            throw ApiException.conflict("Genre name already exists: " + request.genreName());
        }
        genre.setGenreName(request.genreName());
        genre.setDescription(request.description());
        return GenreResponse.from(genreRepository.save(genre));
    }

    public void delete(String id) {
        Genre genre = find(id);
        if (movieRepository.existsByGenreId(id)) {
            throw ApiException.conflict("Cannot delete genre that still has movies");
        }
        genreRepository.delete(genre);
    }

    Genre find(String id) {
        return genreRepository.findById(id)
                .orElseThrow(() -> ApiException.notFound("Genre not found with id: " + id));
    }
}
""",
    "service/RoomService.java": """package com.fudn.movieservice.service;

import com.fudn.movieservice.dto.RoomRequest;
import com.fudn.movieservice.dto.RoomResponse;
import com.fudn.movieservice.exception.ApiException;
import com.fudn.movieservice.model.CinemaRoom;
import com.fudn.movieservice.repository.RoomRepository;
import com.fudn.movieservice.repository.ShowtimeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class RoomService {

    private final RoomRepository roomRepository;
    private final ShowtimeRepository showtimeRepository;

    public List<RoomResponse> getAll() {
        return roomRepository.findAll(Sort.by("roomName")).stream().map(RoomResponse::from).toList();
    }

    public RoomResponse getById(String id) {
        return RoomResponse.from(find(id));
    }

    public RoomResponse create(RoomRequest request) {
        if (roomRepository.existsByRoomNameIgnoreCase(request.roomName())) {
            throw ApiException.conflict("Room name already exists: " + request.roomName());
        }
        CinemaRoom room = new CinemaRoom();
        apply(room, request);
        return RoomResponse.from(roomRepository.save(room));
    }

    public RoomResponse update(String id, RoomRequest request) {
        CinemaRoom room = find(id);
        if (roomRepository.existsByRoomNameIgnoreCaseAndRoomIdNot(request.roomName(), id)) {
            throw ApiException.conflict("Room name already exists: " + request.roomName());
        }
        apply(room, request);
        return RoomResponse.from(roomRepository.save(room));
    }

    public void delete(String id) {
        CinemaRoom room = find(id);
        if (showtimeRepository.existsByRoomId(id)) {
            throw ApiException.conflict("Cannot delete room that already has showtimes");
        }
        roomRepository.delete(room);
    }

    CinemaRoom find(String id) {
        return roomRepository.findById(id)
                .orElseThrow(() -> ApiException.notFound("Room not found with id: " + id));
    }

    private void apply(CinemaRoom room, RoomRequest request) {
        room.setRoomName(request.roomName());
        room.setRoomType(request.roomType());
        room.setSeatRows(request.seatRows());
        room.setSeatsPerRow(request.seatsPerRow());
        room.setRoomStatus(request.roomStatus());
    }
}
""",
    "service/MovieService.java": """package com.fudn.movieservice.service;

import com.fudn.movieservice.dto.MovieRequest;
import com.fudn.movieservice.dto.MovieResponse;
import com.fudn.movieservice.exception.ApiException;
import com.fudn.movieservice.model.Genre;
import com.fudn.movieservice.model.Movie;
import com.fudn.movieservice.model.MovieStatus;
import com.fudn.movieservice.repository.GenreRepository;
import com.fudn.movieservice.repository.MovieRepository;
import com.fudn.movieservice.repository.ShowtimeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class MovieService {

    private final MovieRepository movieRepository;
    private final GenreRepository genreRepository;
    private final ShowtimeRepository showtimeRepository;
    private final GenreService genreService;
    private final MongoTemplate mongoTemplate;

    public List<MovieResponse> search(String keyword, String genreId, MovieStatus status) {
        Query query = new Query();
        if (keyword != null && !keyword.isBlank()) {
            query.addCriteria(Criteria.where("title").regex(Pattern.quote(keyword.trim()), "i"));
        }
        if (genreId != null && !genreId.isBlank()) {
            query.addCriteria(Criteria.where("genreId").is(genreId));
        }
        if (status != null) {
            query.addCriteria(Criteria.where("movieStatus").is(status));
        }
        query.with(Sort.by("title"));
        return toResponses(mongoTemplate.find(query, Movie.class));
    }

    public MovieResponse getById(String id) {
        Movie movie = find(id);
        return MovieResponse.from(movie, genreService.find(movie.getGenreId()).getGenreName());
    }

    public MovieResponse create(MovieRequest request) {
        Movie movie = new Movie();
        Genre genre = apply(movie, request);
        return MovieResponse.from(movieRepository.save(movie), genre.getGenreName());
    }

    public MovieResponse update(String id, MovieRequest request) {
        Movie movie = find(id);
        Genre genre = apply(movie, request);
        return MovieResponse.from(movieRepository.save(movie), genre.getGenreName());
    }

    public void delete(String id) {
        Movie movie = find(id);
        if (showtimeRepository.existsByMovieId(id)) {
            throw ApiException.conflict("Cannot delete movie that already has showtimes");
        }
        movieRepository.delete(movie);
    }

    public Movie find(String id) {
        return movieRepository.findById(id)
                .orElseThrow(() -> ApiException.notFound("Movie not found with id: " + id));
    }

    private List<MovieResponse> toResponses(List<Movie> movies) {
        Map<String, String> genreNames = genreRepository.findAll().stream()
                .collect(Collectors.toMap(Genre::getGenreId, Genre::getGenreName));
        return movies.stream()
                .map(m -> MovieResponse.from(m, genreNames.get(m.getGenreId())))
                .toList();
    }

    private Genre apply(Movie movie, MovieRequest request) {
        Genre genre = genreService.find(request.genreId());
        movie.setTitle(request.title());
        movie.setDescription(request.description());
        movie.setDirector(request.director());
        movie.setDurationMinutes(request.durationMinutes());
        movie.setLanguage(request.language());
        movie.setAgeRating(request.ageRating());
        movie.setReleaseDate(request.releaseDate());
        movie.setGenreId(genre.getGenreId());
        movie.setMovieStatus(request.movieStatus());
        return genre;
    }
}
""",
    "service/ShowtimeService.java": """package com.fudn.movieservice.service;

import com.fudn.movieservice.dto.ShowtimeRequest;
import com.fudn.movieservice.dto.ShowtimeResponse;
import com.fudn.movieservice.exception.ApiException;
import com.fudn.movieservice.model.*;
import com.fudn.movieservice.repository.MovieRepository;
import com.fudn.movieservice.repository.RoomRepository;
import com.fudn.movieservice.repository.ShowtimeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ShowtimeService {

    private static final String NO_EXCLUDE = "";

    private final ShowtimeRepository showtimeRepository;
    private final MovieRepository movieRepository;
    private final RoomRepository roomRepository;
    private final MovieService movieService;
    private final RoomService roomService;

    public List<ShowtimeResponse> search(String movieId, LocalDate date) {
        List<Showtime> showtimes = (movieId == null || movieId.isBlank())
                ? showtimeRepository.findAllByOrderByStartTimeAsc()
                : showtimeRepository.findByMovieIdOrderByStartTimeAsc(movieId);
        List<Showtime> filtered = showtimes.stream()
                .filter(s -> date == null || s.getStartTime().toLocalDate().equals(date))
                .toList();
        return toResponses(filtered);
    }

    public ShowtimeResponse getById(String id) {
        Showtime s = find(id);
        return ShowtimeResponse.from(s, movieService.find(s.getMovieId()), roomService.find(s.getRoomId()));
    }

    public ShowtimeResponse create(ShowtimeRequest request) {
        Showtime showtime = new Showtime();
        showtime.setShowtimeStatus(ShowtimeStatus.SCHEDULED);
        return apply(showtime, request, NO_EXCLUDE);
    }

    public ShowtimeResponse update(String id, ShowtimeRequest request) {
        Showtime showtime = find(id);
        if (showtime.getShowtimeStatus() == ShowtimeStatus.CANCELLED) {
            throw ApiException.badRequest("Cannot update a cancelled showtime");
        }
        return apply(showtime, request, id);
    }

    public void cancel(String id) {
        Showtime showtime = find(id);
        showtime.setShowtimeStatus(ShowtimeStatus.CANCELLED);
        showtimeRepository.save(showtime);
    }

    private Showtime find(String id) {
        return showtimeRepository.findById(id)
                .orElseThrow(() -> ApiException.notFound("Showtime not found with id: " + id));
    }

    private ShowtimeResponse apply(Showtime showtime, ShowtimeRequest request, String excludeId) {
        Movie movie = movieService.find(request.movieId());
        CinemaRoom room = roomService.find(request.roomId());

        if (movie.getMovieStatus() == MovieStatus.ENDED) {
            throw ApiException.badRequest("Movie '" + movie.getTitle() + "' has ENDED and cannot be scheduled");
        }
        if (room.getRoomStatus() != RoomStatus.ACTIVE) {
            throw ApiException.badRequest("Room '" + room.getRoomName() + "' is not ACTIVE");
        }
        if (!request.startTime().isAfter(LocalDateTime.now())) {
            throw ApiException.badRequest("Start time must be in the future");
        }
        LocalDateTime endTime = request.startTime().plusMinutes(movie.getDurationMinutes());

        long overlaps = showtimeRepository
                .countByRoomIdAndShowtimeStatusAndStartTimeLessThanAndEndTimeGreaterThanAndShowtimeIdNot(
                        room.getRoomId(), ShowtimeStatus.SCHEDULED, endTime, request.startTime(), excludeId);
        if (overlaps > 0) {
            throw ApiException.conflict("Room '" + room.getRoomName() + "' already has a showtime between "
                    + request.startTime() + " and " + endTime);
        }

        showtime.setMovieId(movie.getMovieId());
        showtime.setRoomId(room.getRoomId());
        showtime.setStartTime(request.startTime());
        showtime.setEndTime(endTime);
        showtime.setTicketPrice(request.ticketPrice());
        return ShowtimeResponse.from(showtimeRepository.save(showtime), movie, room);
    }

    private List<ShowtimeResponse> toResponses(List<Showtime> showtimes) {
        Map<String, Movie> movies = movieRepository
                .findAllById(showtimes.stream().map(Showtime::getMovieId).distinct().toList())
                .stream().collect(Collectors.toMap(Movie::getMovieId, Function.identity()));
        Map<String, CinemaRoom> rooms = roomRepository
                .findAllById(showtimes.stream().map(Showtime::getRoomId).distinct().toList())
                .stream().collect(Collectors.toMap(CinemaRoom::getRoomId, Function.identity()));
        return showtimes.stream()
                .map(s -> ShowtimeResponse.from(s, movies.get(s.getMovieId()), rooms.get(s.getRoomId())))
                .toList();
    }
}
""",
    "config/DataSeeder.java": """package com.fudn.movieservice.config;

import com.fudn.movieservice.model.*;
import com.fudn.movieservice.repository.GenreRepository;
import com.fudn.movieservice.repository.MovieRepository;
import com.fudn.movieservice.repository.RoomRepository;
import com.fudn.movieservice.repository.ShowtimeRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Slf4j
@Component
@RequiredArgsConstructor
public class DataSeeder implements CommandLineRunner {

    public static final String GENRE_ACTION = "66f000000000000000000001";
    public static final String GENRE_ANIMATION = "66f000000000000000000002";
    public static final String GENRE_HORROR = "66f000000000000000000003";
    public static final String GENRE_ROMANCE = "66f000000000000000000004";
    public static final String GENRE_SCIFI = "66f000000000000000000005";

    public static final String ROOM_01 = "66f100000000000000000001";
    public static final String ROOM_02 = "66f100000000000000000002";
    public static final String ROOM_IMAX = "66f100000000000000000003";
    public static final String ROOM_04_MAINTENANCE = "66f100000000000000000004";

    public static final String MOVIE_GALAXY = "66f200000000000000000001";
    public static final String MOVIE_HAUNTED = "66f200000000000000000002";
    public static final String MOVIE_ROBOT = "66f200000000000000000003";
    public static final String MOVIE_SUMMER_ENDED = "66f200000000000000000004";

    private final GenreRepository genreRepository;
    private final RoomRepository roomRepository;
    private final MovieRepository movieRepository;
    private final ShowtimeRepository showtimeRepository;

    @Override
    public void run(String... args) {
        if (genreRepository.count() > 0) {
            log.info("MongoDB already has seed data - skip seeding");
            return;
        }

        genreRepository.saveAll(List.of(
                new Genre(GENRE_ACTION, "Hành động", "Phim hành động, võ thuật"),
                new Genre(GENRE_ANIMATION, "Hoạt hình", "Phim hoạt hình cho mọi lứa tuổi"),
                new Genre(GENRE_HORROR, "Kinh dị", "Phim kinh dị, giật gân"),
                new Genre(GENRE_ROMANCE, "Tình cảm", "Phim tình cảm, lãng mạn"),
                new Genre(GENRE_SCIFI, "Khoa học viễn tưởng", "Phim khoa học viễn tưởng")));

        roomRepository.saveAll(List.of(
                new CinemaRoom(ROOM_01, "Room 01", RoomType.STANDARD, 8, 10, RoomStatus.ACTIVE),
                new CinemaRoom(ROOM_02, "Room 02", RoomType.THREE_D, 6, 8, RoomStatus.ACTIVE),
                new CinemaRoom(ROOM_IMAX, "IMAX 01", RoomType.IMAX, 10, 12, RoomStatus.ACTIVE),
                new CinemaRoom(ROOM_04_MAINTENANCE, "Room 04", RoomType.STANDARD, 5, 8, RoomStatus.MAINTENANCE)));

        movieRepository.saveAll(List.of(
                new Movie(MOVIE_GALAXY, "Galaxy Rangers", "Đội biệt kích không gian bảo vệ dải ngân hà.",
                        "John Carter", 125, "English", AgeRating.T13, LocalDate.of(2026, 9, 20),
                        GENRE_SCIFI, MovieStatus.NOW_SHOWING),
                new Movie(MOVIE_HAUNTED, "Ngôi Nhà Ma Ám", "Một gia đình chuyển đến căn nhà cổ ở Đà Lạt.",
                        "Trần Hữu Tấn", 100, "Tiếng Việt", AgeRating.T18, LocalDate.of(2026, 9, 27),
                        GENRE_HORROR, MovieStatus.NOW_SHOWING),
                new Movie(MOVIE_ROBOT, "Robot Nhỏ Phiêu Lưu Ký", "Chú robot nhỏ đi tìm đường về nhà.",
                        "Anna Lee", 95, "English", AgeRating.P, LocalDate.of(2026, 11, 15),
                        GENRE_ANIMATION, MovieStatus.COMING_SOON),
                new Movie(MOVIE_SUMMER_ENDED, "Mùa Hè Năm Ấy", "Câu chuyện tình đầu tuổi học trò.",
                        "Nguyễn Quang Dũng", 110, "Tiếng Việt", AgeRating.T16, LocalDate.of(2026, 6, 1),
                        GENRE_ROMANCE, MovieStatus.ENDED)));

        showtimeRepository.saveAll(List.of(
                showtime("66f300000000000000000001", MOVIE_GALAXY, ROOM_01, "2026-12-20T19:00", 125, 95000, ShowtimeStatus.SCHEDULED),
                showtime("66f300000000000000000002", MOVIE_GALAXY, ROOM_IMAX, "2026-12-20T20:00", 125, 150000, ShowtimeStatus.SCHEDULED),
                showtime("66f300000000000000000003", MOVIE_HAUNTED, ROOM_02, "2026-12-21T21:00", 100, 95000, ShowtimeStatus.SCHEDULED),
                showtime("66f300000000000000000004", MOVIE_ROBOT, ROOM_01, "2026-12-22T09:00", 95, 75000, ShowtimeStatus.SCHEDULED),
                showtime("66f300000000000000000005", MOVIE_HAUNTED, ROOM_01, "2026-12-23T19:00", 100, 95000, ShowtimeStatus.CANCELLED)));

        log.info("Seeded MongoDB: {} genres, {} rooms, {} movies, {} showtimes",
                genreRepository.count(), roomRepository.count(), movieRepository.count(), showtimeRepository.count());
    }

    private static Showtime showtime(String id, String movieId, String roomId, String start,
                                     int durationMinutes, long price, ShowtimeStatus status) {
        LocalDateTime startTime = LocalDateTime.parse(start);
        return new Showtime(id, movieId, roomId, startTime, startTime.plusMinutes(durationMinutes),
                BigDecimal.valueOf(price), status);
    }
}
""",
    "controller/GenreController.java": """package com.fudn.movieservice.controller;

import com.fudn.movieservice.dto.GenreRequest;
import com.fudn.movieservice.dto.GenreResponse;
import com.fudn.movieservice.service.GenreService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/genres")
@RequiredArgsConstructor
public class GenreController {

    private final GenreService genreService;

    @GetMapping
    public List<GenreResponse> getAll() {
        return genreService.getAll();
    }

    @GetMapping("/{id}")
    public GenreResponse getById(@PathVariable String id) {
        return genreService.getById(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public GenreResponse create(@Valid @RequestBody GenreRequest request) {
        return genreService.create(request);
    }

    @PutMapping("/{id}")
    public GenreResponse update(@PathVariable String id, @Valid @RequestBody GenreRequest request) {
        return genreService.update(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable String id) {
        genreService.delete(id);
    }
}
""",
    "controller/RoomController.java": """package com.fudn.movieservice.controller;

import com.fudn.movieservice.dto.RoomRequest;
import com.fudn.movieservice.dto.RoomResponse;
import com.fudn.movieservice.service.RoomService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/rooms")
@RequiredArgsConstructor
public class RoomController {

    private final RoomService roomService;

    @GetMapping
    public List<RoomResponse> getAll() {
        return roomService.getAll();
    }

    @GetMapping("/{id}")
    public RoomResponse getById(@PathVariable String id) {
        return roomService.getById(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public RoomResponse create(@Valid @RequestBody RoomRequest request) {
        return roomService.create(request);
    }

    @PutMapping("/{id}")
    public RoomResponse update(@PathVariable String id, @Valid @RequestBody RoomRequest request) {
        return roomService.update(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable String id) {
        roomService.delete(id);
    }
}
""",
    "controller/MovieController.java": """package com.fudn.movieservice.controller;

import com.fudn.movieservice.dto.MovieRequest;
import com.fudn.movieservice.dto.MovieResponse;
import com.fudn.movieservice.model.MovieStatus;
import com.fudn.movieservice.service.MovieService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/movies")
@RequiredArgsConstructor
public class MovieController {

    private final MovieService movieService;

    @GetMapping
    public List<MovieResponse> search(@RequestParam(required = false) String keyword,
                                      @RequestParam(required = false) String genreId,
                                      @RequestParam(required = false) MovieStatus status) {
        return movieService.search(keyword, genreId, status);
    }

    @GetMapping("/{id}")
    public MovieResponse getById(@PathVariable String id) {
        return movieService.getById(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public MovieResponse create(@Valid @RequestBody MovieRequest request) {
        return movieService.create(request);
    }

    @PutMapping("/{id}")
    public MovieResponse update(@PathVariable String id, @Valid @RequestBody MovieRequest request) {
        return movieService.update(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable String id) {
        movieService.delete(id);
    }
}
""",
    "controller/ShowtimeController.java": """package com.fudn.movieservice.controller;

import com.fudn.movieservice.dto.ShowtimeRequest;
import com.fudn.movieservice.dto.ShowtimeResponse;
import com.fudn.movieservice.service.ShowtimeService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/showtimes")
@RequiredArgsConstructor
public class ShowtimeController {

    private final ShowtimeService showtimeService;

    @GetMapping
    public List<ShowtimeResponse> search(
            @RequestParam(required = false) String movieId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        return showtimeService.search(movieId, date);
    }

    @GetMapping("/{id}")
    public ShowtimeResponse getById(@PathVariable String id) {
        return showtimeService.getById(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ShowtimeResponse create(@Valid @RequestBody ShowtimeRequest request) {
        return showtimeService.create(request);
    }

    @PutMapping("/{id}")
    public ShowtimeResponse update(@PathVariable String id, @Valid @RequestBody ShowtimeRequest request) {
        return showtimeService.update(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void cancel(@PathVariable String id) {
        showtimeService.cancel(id);
    }
}
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {rel_path}")

print("All movie-service files created successfully!")
