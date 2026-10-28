package fu.de190353.userservice.service.impl;

import fu.de190353.userservice.dto.ApiResponse;
import fu.de190353.userservice.dto.PageDTO;
import fu.de190353.userservice.dto.UserDTO;
import fu.de190353.userservice.entity.Role;
import fu.de190353.userservice.entity.User;
import fu.de190353.userservice.entity.UserStatus;
import fu.de190353.userservice.repository.UserRepository;
import fu.de190353.userservice.service.UserService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;

    public UserServiceImpl(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    @Transactional
    public ApiResponse createUser(UserDTO dto) {
        // status = 3 -> duplicated username
        if (userRepository.existsByUsername(dto.getUsername())) {
            return ApiResponse.error(3, "Username is duplicated");
        }

        User user = new User();
        user.setUsername(dto.getUsername());
        user.setEmail(dto.getEmail());
        user.setRole(Role.valueOf(dto.getRole()));
        user.setRatePerPost(dto.getRatePerPost());
        user.setMaxDailyPosts(dto.getMaxDailyPosts());
        user.setLevel(dto.getLevel());
        // Default status is ACTIVE when not provided
        user.setStatus(dto.getStatus() == null ? UserStatus.ACTIVE : UserStatus.valueOf(dto.getStatus()));

        User saved = userRepository.save(user);
        return ApiResponse.ok("User created successfully", toDTO(saved));
    }

    @Override
    @Transactional
    public ApiResponse updateUser(Long userId, UserDTO dto) {
        User user = userRepository.findById(userId).orElse(null);
        if (user == null) {
            return ApiResponse.error(4, "User is not found");
        }

        // Duplicated username (excluding current user)
        if (dto.getUsername() != null
                && userRepository.existsByUsernameAndIdNot(dto.getUsername(), userId)) {
            return ApiResponse.error(3, "Username is duplicated");
        }

        // Partial update: only non-null fields
        if (dto.getUsername() != null)      user.setUsername(dto.getUsername());
        if (dto.getEmail() != null)         user.setEmail(dto.getEmail());
        if (dto.getRole() != null)          user.setRole(Role.valueOf(dto.getRole()));
        if (dto.getRatePerPost() != null)   user.setRatePerPost(dto.getRatePerPost());
        if (dto.getMaxDailyPosts() != null) user.setMaxDailyPosts(dto.getMaxDailyPosts());
        if (dto.getLevel() != null)         user.setLevel(dto.getLevel());
        if (dto.getStatus() != null)        user.setStatus(UserStatus.valueOf(dto.getStatus()));

        User saved = userRepository.save(user);
        return ApiResponse.ok("User updated successfully", toDTO(saved));
    }

    @Override
    @Transactional(readOnly = true)
    public ApiResponse getUserById(Long userId) {
        User user = userRepository.findById(userId).orElse(null);
        if (user == null) {
            return ApiResponse.error(4, "User is not found");
        }
        return ApiResponse.ok("Successful", toDTO(user));
    }

    @Override
    @Transactional
    public ApiResponse deactivateUser(Long userId) {
        User user = userRepository.findById(userId).orElse(null);
        if (user == null) {
            return ApiResponse.error(4, "User is not found");
        }
        user.setStatus(UserStatus.DEACTIVATED);
        userRepository.save(user);
        return ApiResponse.ok("User is set to DEACTIVATED successfully", null);
    }

    @Override
    @Transactional(readOnly = true)
    public ApiResponse getUserList(String role, String status, Pageable pageable) {
        Page<User> page = userRepository.search(parseRole(role), parseStatus(status), pageable);
        List<UserDTO> content = page.getContent().stream().map(this::toDTO).toList();
        PageDTO pageDTO = new PageDTO(
                page.getSize(), page.getNumber(), page.getTotalPages(),
                page.getTotalElements(), page.isFirst(), page.isLast(), content);
        return ApiResponse.ok("Successful", pageDTO);
    }

    // -- helpers --
    private UserDTO toDTO(User u) {
        UserDTO d = new UserDTO();
        d.setUserId(u.getId());
        d.setUsername(u.getUsername());
        d.setEmail(u.getEmail());
        d.setRole(u.getRole().name());
        d.setRatePerPost(u.getRatePerPost());
        d.setMaxDailyPosts(u.getMaxDailyPosts());
        d.setLevel(u.getLevel());
        d.setStatus(u.getStatus().name());
        return d;
    }

    // Parse filter string -> enum; tra null neu rong/khong hop le (bo qua filter)
    private Role parseRole(String s) {
        if (s == null || s.isBlank()) return null;
        try { return Role.valueOf(s); } catch (IllegalArgumentException e) { return null; }
    }

    private UserStatus parseStatus(String s) {
        if (s == null || s.isBlank()) return null;
        try { return UserStatus.valueOf(s); } catch (IllegalArgumentException e) { return null; }
    }
}
