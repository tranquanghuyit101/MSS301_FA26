package fu.de190353.userservice.dto;

import fu.de190353.userservice.common.UserConstants;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;

public class UserDTO {

    private Long userId;

    @NotBlank(message = "Username is required")
    @Size(max = 30, message = "Username max length is 30")
    private String username;

    @NotBlank(message = "Email is required")
    @Email(message = "Email is invalid")
    @Size(max = 100, message = "Email max length is 100")
    private String email;

    @NotBlank(message = "Role is required")
    @Pattern(regexp = UserConstants.ROLE_REGEX, message = "Role must be USER, CREATOR, or ADMIN")
    private String role;

    @NotNull(message = "ratePerPost is required")
    @DecimalMin(value = "0", inclusive = false, message = "ratePerPost must be > 0")
    private BigDecimal ratePerPost;

    @NotNull(message = "maxDailyPosts is required")
    @Min(value = 1, message = "maxDailyPosts must be >= 1")
    @Max(value = 10, message = "maxDailyPosts must be <= 10")
    private Integer maxDailyPosts;

    @NotNull(message = "level is required")
    @Min(value = 1, message = "level must be >= 1")
    private Integer level;

    // Optional on create (defaults to ACTIVE); validated only when present
    @Pattern(regexp = UserConstants.STATUS_REGEX, message = "status must be ACTIVE, SUSPENDED or DEACTIVATED")
    private String status;

    public UserDTO() {}

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public BigDecimal getRatePerPost() { return ratePerPost; }
    public void setRatePerPost(BigDecimal ratePerPost) { this.ratePerPost = ratePerPost; }

    public Integer getMaxDailyPosts() { return maxDailyPosts; }
    public void setMaxDailyPosts(Integer maxDailyPosts) { this.maxDailyPosts = maxDailyPosts; }

    public Integer getLevel() { return level; }
    public void setLevel(Integer level) { this.level = level; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
