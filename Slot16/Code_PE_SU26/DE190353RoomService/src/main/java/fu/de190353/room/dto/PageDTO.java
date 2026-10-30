package fu.de190353.room.dto;

public class PageDTO {
    private int size;
    private int page;
    private int totalPages;
    private long totalElements;
    private boolean first;
    private boolean last;
    private Object content; // List<RoomDTO>

    public PageDTO() {}

    public PageDTO(int size, int page, int totalPages, long totalElements, boolean first, boolean last, Object content) {
        this.size = size;
        this.page = page;
        this.totalPages = totalPages;
        this.totalElements = totalElements;
        this.first = first;
        this.last = last;
        this.content = content;
    }

    public int getSize() { return size; }
    public void setSize(int size) { this.size = size; }

    public int getPage() { return page; }
    public void setPage(int page) { this.page = page; }

    public int getTotalPages() { return totalPages; }
    public void setTotalPages(int totalPages) { this.totalPages = totalPages; }

    public long getTotalElements() { return totalElements; }
    public void setTotalElements(long totalElements) { this.totalElements = totalElements; }

    public boolean isFirst() { return first; }
    public void setFirst(boolean first) { this.first = first; }

    public boolean isLast() { return last; }
    public void setLast(boolean last) { this.last = last; }

    public Object getContent() { return content; }
    public void setContent(Object content) { this.content = content; }
}
