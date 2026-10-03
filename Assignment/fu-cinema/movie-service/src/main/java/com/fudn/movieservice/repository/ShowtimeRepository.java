package com.fudn.movieservice.repository;

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
