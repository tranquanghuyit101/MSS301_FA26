package fu.de190353.userservice.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    private Long id;

    @Column(name = "username", nullable = false, length = 30, unique = true)
    private String username;

    @Column(name = "email", nullable = false, length = 100, unique = true)
    private String email;

    @Enumerated(EnumType.STRING)
    @Column(name = "role", nullable = false, length = 15)
    private Role role;

    @Column(name = "rate_per_post", nullable = false, precision = 18, scale = 2)
    private BigDecimal ratePerPost;

    @Column(name = "max_daily_posts", nullable = false)
    private Integer maxDailyPosts;

    @Column(name = "level", nullable = false)
    private Integer level;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 15)
    private UserStatus status;

    public User() {}

    public User(Long id, String username, String email, Role role, BigDecimal ratePerPost, Integer maxDailyPosts, Integer level, UserStatus status) {
        this.id = id;
        this.username = username;
        this.email = email;
        this.role = role;
        this.ratePerPost = ratePerPost;
        this.maxDailyPosts = maxDailyPosts;
        this.level = level;
        this.status = status;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public Role getRole() { return role; }
    public void setRole(Role role) { this.role = role; }

    public BigDecimal getRatePerPost() { return ratePerPost; }
    public void setRatePerPost(BigDecimal ratePerPost) { this.ratePerPost = ratePerPost; }

    public Integer getMaxDailyPosts() { return maxDailyPosts; }
    public void setMaxDailyPosts(Integer maxDailyPosts) { this.maxDailyPosts = maxDailyPosts; }

    public Integer getLevel() { return level; }
    public void setLevel(Integer level) { this.level = level; }

    public UserStatus getStatus() { return status; }
    public void setStatus(UserStatus status) { this.status = status; }
}
