package fu.de190353.reservation.repository;

import fu.de190353.reservation.entity.Reservation;
import fu.de190353.reservation.entity.ReservationStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ReservationRepository extends JpaRepository<Reservation, Long> {

    @Query("""
            SELECT r FROM Reservation r
            WHERE (:guestName IS NULL OR LOWER(r.guestName) LIKE LOWER(CONCAT('%', :guestName, '%')))
              AND (:status IS NULL OR r.status = :status)
            """)
    Page<Reservation> search(@Param("guestName") String guestName,
                             @Param("status") ReservationStatus status,
                             Pageable pageable);
}
