package fu.de190353.postservice.common;

public final class PostConstants {
    private PostConstants() {}

    public static final String DRAFT = "DRAFT";
    public static final String SCHEDULED = "SCHEDULED";
    public static final String PUBLISHED = "PUBLISHED";
    public static final String CANCELLED = "CANCELLED";

    public static final String STATUS_REGEX = "DRAFT|SCHEDULED|PUBLISHED|CANCELLED";

    // User status coming from UserService
    public static final String USER_ACTIVE = "ACTIVE";
}
