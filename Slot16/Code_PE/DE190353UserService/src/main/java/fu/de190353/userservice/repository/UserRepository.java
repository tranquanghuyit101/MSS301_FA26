package fu.de190353.userservice.repository;

import fu.de190353.userservice.entity.Role;
import fu.de190353.userservice.entity.User;
import fu.de190353.userservice.entity.UserStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface UserRepository extends JpaRepository<User, Long> {
    boolean existsByUsername(String username);
    boolean existsByUsernameAndIdNot(String username, Long id);

    // Null-safe filter: when a param is null it is ignored
    @Query("""
            SELECT u FROM User u
            WHERE (:role   IS NULL OR u.role   = :role)
              AND (:status IS NULL OR u.status = :status)
            """)
    Page<User> search(@Param("role") Role role,
                      @Param("status") UserStatus status,
                      Pageable pageable);
}
