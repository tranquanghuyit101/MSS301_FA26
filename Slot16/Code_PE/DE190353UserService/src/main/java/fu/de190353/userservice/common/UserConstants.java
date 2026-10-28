package fu.de190353.userservice.common;

public final class UserConstants {
    private UserConstants() {}

    // User status
    public static final String ACTIVE = "ACTIVE";
    public static final String SUSPENDED = "SUSPENDED";
    public static final String DEACTIVATED = "DEACTIVATED";

    // Regex for validation
    public static final String ROLE_REGEX = "USER|CREATOR|ADMIN";
    public static final String STATUS_REGEX = "ACTIVE|SUSPENDED|DEACTIVATED";
}
