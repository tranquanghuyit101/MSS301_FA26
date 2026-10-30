package fu.de190353.room.service.impl;

import fu.de190353.room.dto.ApiResponseDTO;
import fu.de190353.room.dto.PageDTO;
import fu.de190353.room.dto.RoomDTO;
import fu.de190353.room.entity.Room;
import fu.de190353.room.entity.RoomStatus;
import fu.de190353.room.entity.RoomType;
import fu.de190353.room.repository.RoomRepository;
import fu.de190353.room.service.RoomService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class RoomServiceImpl implements RoomService {

    private final RoomRepository roomRepository;

    public RoomServiceImpl(RoomRepository roomRepository) {
        this.roomRepository = roomRepository;
    }

    @Override
    @Transactional
    public ApiResponseDTO createRoom(RoomDTO dto) {
        // status = 3 -> duplicated room number
        if (roomRepository.existsByRoomNumber(dto.getRoomNumber())) {
            return ApiResponseDTO.error(3, "Room number is duplicated");
        }

        Room room = new Room();
        room.setRoomNumber(dto.getRoomNumber());
        room.setRoomType(RoomType.valueOf(dto.getRoomType()));
        room.setPricePerNight(dto.getPricePerNight());
        room.setCapacity(dto.getCapacity());
        room.setFloor(dto.getFloor());
        // Default status is AVAILABLE when not provided
        room.setStatus(dto.getStatus() == null || dto.getStatus().isBlank()
                ? RoomStatus.AVAILABLE
                : RoomStatus.valueOf(dto.getStatus()));

        Room saved = roomRepository.save(room);
        return ApiResponseDTO.ok("Room created successfully", toDTO(saved));
    }

    @Override
    @Transactional
    public ApiResponseDTO updateRoom(Long roomId, RoomDTO dto) {
        Room room = roomRepository.findById(roomId).orElse(null);
        if (room == null) {
            return ApiResponseDTO.error(4, "Room is not found");
        }

        // Duplicated room number (excluding current room)
        if (dto.getRoomNumber() != null
                && roomRepository.existsByRoomNumberAndRoomIdNot(dto.getRoomNumber(), roomId)) {
            return ApiResponseDTO.error(3, "Room number is duplicated");
        }

        // Partial update: only non-null fields
        if (dto.getRoomNumber() != null)    room.setRoomNumber(dto.getRoomNumber());
        if (dto.getRoomType() != null)      room.setRoomType(RoomType.valueOf(dto.getRoomType()));
        if (dto.getPricePerNight() != null) room.setPricePerNight(dto.getPricePerNight());
        if (dto.getCapacity() != null)      room.setCapacity(dto.getCapacity());
        if (dto.getFloor() != null)         room.setFloor(dto.getFloor());
        if (dto.getStatus() != null)        room.setStatus(RoomStatus.valueOf(dto.getStatus()));

        Room saved = roomRepository.save(room);
        return ApiResponseDTO.ok("Room updated successfully", toDTO(saved));
    }

    @Override
    @Transactional(readOnly = true)
    public ApiResponseDTO getRoomById(Long roomId) {
        Room room = roomRepository.findById(roomId).orElse(null);
        if (room == null) {
            return ApiResponseDTO.error(4, "Room is not found");
        }
        return ApiResponseDTO.ok("Successful", toDTO(room));
    }

    @Override
    @Transactional
    public ApiResponseDTO setRoomToMaintenance(Long roomId) {
        Room room = roomRepository.findById(roomId).orElse(null);
        if (room == null) {
            return ApiResponseDTO.error(4, "Room is not found");
        }
        room.setStatus(RoomStatus.MAINTENANCE);
        roomRepository.save(room);
        return ApiResponseDTO.ok("Room set to MAINTENANCE successfully", null);
    }

    @Override
    @Transactional(readOnly = true)
    public ApiResponseDTO getRoomList(String roomType, String status, Pageable pageable) {
        Page<Room> page = roomRepository.search(parseRoomType(roomType), parseRoomStatus(status), pageable);
        List<RoomDTO> content = page.getContent().stream().map(this::toDTO).toList();
        PageDTO pageDTO = new PageDTO(
                page.getSize(), page.getNumber(), page.getTotalPages(),
                page.getTotalElements(), page.isFirst(), page.isLast(), content);
        return ApiResponseDTO.ok("Successful", pageDTO);
    }

    // -- helpers --
    private RoomDTO toDTO(Room r) {
        RoomDTO d = new RoomDTO();
        d.setRoomId(r.getRoomId());
        d.setRoomNumber(r.getRoomNumber());
        d.setRoomType(r.getRoomType().name());
        d.setPricePerNight(r.getPricePerNight());
        d.setCapacity(r.getCapacity());
        d.setFloor(r.getFloor());
        d.setStatus(r.getStatus().name());
        return d;
    }

    private RoomType parseRoomType(String s) {
        if (s == null || s.isBlank()) return null;
        try { return RoomType.valueOf(s); } catch (IllegalArgumentException e) { return null; }
    }

    private RoomStatus parseRoomStatus(String s) {
        if (s == null || s.isBlank()) return null;
        try { return RoomStatus.valueOf(s); } catch (IllegalArgumentException e) { return null; }
    }
}
