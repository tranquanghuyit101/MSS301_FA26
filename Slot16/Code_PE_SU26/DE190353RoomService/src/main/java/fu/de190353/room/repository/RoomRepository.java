package fu.de190353.room.repository;

import fu.de190353.room.entity.Room;
import fu.de190353.room.entity.RoomStatus;
import fu.de190353.room.entity.RoomType;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface RoomRepository extends JpaRepository<Room, Long> {

    boolean existsByRoomNumber(String roomNumber);

    boolean existsByRoomNumberAndRoomIdNot(String roomNumber, Long roomId);

    // Null-safe search query
    @Query("""
            SELECT r FROM Room r
            WHERE (:roomType IS NULL OR r.roomType = :roomType)
              AND (:status IS NULL OR r.status = :status)
            """)
    Page<Room> search(@Param("roomType") RoomType roomType,
                      @Param("status") RoomStatus status,
                      Pageable pageable);
}
