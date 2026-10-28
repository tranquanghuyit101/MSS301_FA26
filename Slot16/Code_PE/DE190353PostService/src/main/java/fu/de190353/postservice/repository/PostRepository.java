package fu.de190353.postservice.repository;

import fu.de190353.postservice.entity.Post;
import fu.de190353.postservice.entity.PostStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface PostRepository extends JpaRepository<Post, Long> {

    @Query("""
            SELECT p FROM Post p
            WHERE (:advertiserName IS NULL OR LOWER(p.advertiserName) LIKE LOWER(CONCAT('%', :advertiserName, '%')))
              AND (:status IS NULL OR p.status = :status)
            """)
    Page<Post> search(@Param("advertiserName") String advertiserName,
                      @Param("status") PostStatus status,
                      Pageable pageable);
}
