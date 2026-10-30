package fu.de190353.room.dto;

import fu.de190353.room.common.RoomConstants;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;

public class RoomDTO {

    private Long roomId;

    @NotBlank(message = "roomNumber is required")
    @Size(max = 20, message = "roomNumber max length is 20")
    private String roomNumber;

    @NotBlank(message = "roomType is required")
    @Pattern(regexp = RoomConstants.TYPE_REGEX, message = "roomType must be SINGLE, DOUBLE, SUITE, or DELUXE")
    private String roomType;

    @NotNull(message = "pricePerNight is required")
    @DecimalMin(value = "0", inclusive = false, message = "pricePerNight must be > 0")
    private BigDecimal pricePerNight;

    @NotNull(message = "capacity is required")
    @Min(value = 1, message = "capacity must be >= 1")
    @Max(value = 10, message = "capacity must be <= 10")
    private Integer capacity;

    @NotNull(message = "floor is required")
    @Min(value = 1, message = "floor must be >= 1")
    private Integer floor;

    // Optional on create (defaults to AVAILABLE); validated only when present
    @Pattern(regexp = RoomConstants.STATUS_REGEX, message = "status must be AVAILABLE, OCCUPIED, or MAINTENANCE")
    private String status;

    public RoomDTO() {}

    public Long getRoomId() { return roomId; }
    public void setRoomId(Long roomId) { this.roomId = roomId; }

    public String getRoomNumber() { return roomNumber; }
    public void setRoomNumber(String roomNumber) { this.roomNumber = roomNumber; }

    public String getRoomType() { return roomType; }
    public void setRoomType(String roomType) { this.roomType = roomType; }

    public BigDecimal getPricePerNight() { return pricePerNight; }
    public void setPricePerNight(BigDecimal pricePerNight) { this.pricePerNight = pricePerNight; }

    public Integer getCapacity() { return capacity; }
    public void setCapacity(Integer capacity) { this.capacity = capacity; }

    public Integer getFloor() { return floor; }
    public void setFloor(Integer floor) { this.floor = floor; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
