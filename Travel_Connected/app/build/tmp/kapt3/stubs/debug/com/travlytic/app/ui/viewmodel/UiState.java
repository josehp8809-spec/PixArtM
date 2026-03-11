package com.travlytic.app.ui.viewmodel;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00008\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0012\n\u0002\u0010\b\n\u0002\b\u0002\b\u0086\b\u0018\u00002\u00020\u0001BU\u0012\b\b\u0002\u0010\u0002\u001a\u00020\u0003\u0012\u000e\b\u0002\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00060\u0005\u0012\u000e\b\u0002\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\b0\u0005\u0012\u000e\b\u0002\u0010\t\u001a\b\u0012\u0004\u0012\u00020\n0\u0005\u0012\b\b\u0002\u0010\u000b\u001a\u00020\u0003\u0012\n\b\u0002\u0010\f\u001a\u0004\u0018\u00010\r\u00a2\u0006\u0002\u0010\u000eJ\t\u0010\u0016\u001a\u00020\u0003H\u00c6\u0003J\u000f\u0010\u0017\u001a\b\u0012\u0004\u0012\u00020\u00060\u0005H\u00c6\u0003J\u000f\u0010\u0018\u001a\b\u0012\u0004\u0012\u00020\b0\u0005H\u00c6\u0003J\u000f\u0010\u0019\u001a\b\u0012\u0004\u0012\u00020\n0\u0005H\u00c6\u0003J\t\u0010\u001a\u001a\u00020\u0003H\u00c6\u0003J\u000b\u0010\u001b\u001a\u0004\u0018\u00010\rH\u00c6\u0003JY\u0010\u001c\u001a\u00020\u00002\b\b\u0002\u0010\u0002\u001a\u00020\u00032\u000e\b\u0002\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00060\u00052\u000e\b\u0002\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\b0\u00052\u000e\b\u0002\u0010\t\u001a\b\u0012\u0004\u0012\u00020\n0\u00052\b\b\u0002\u0010\u000b\u001a\u00020\u00032\n\b\u0002\u0010\f\u001a\u0004\u0018\u00010\rH\u00c6\u0001J\u0013\u0010\u001d\u001a\u00020\u00032\b\u0010\u001e\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010\u001f\u001a\u00020 H\u00d6\u0001J\t\u0010!\u001a\u00020\rH\u00d6\u0001R\u0011\u0010\u000b\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000b\u0010\u000fR\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0002\u0010\u000fR\u0017\u0010\t\u001a\b\u0012\u0004\u0012\u00020\n0\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0010\u0010\u0011R\u0017\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\b0\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0012\u0010\u0011R\u0017\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00060\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0013\u0010\u0011R\u0013\u0010\f\u001a\u0004\u0018\u00010\r\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0014\u0010\u0015\u00a8\u0006\""}, d2 = {"Lcom/travlytic/app/ui/viewmodel/UiState;", "", "isServiceEnabled", "", "recentLogs", "", "Lcom/travlytic/app/data/db/entities/ResponseLog;", "recentEscalations", "Lcom/travlytic/app/data/db/entities/EscalationLog;", "knowledgeItems", "Lcom/travlytic/app/data/db/entities/KnowledgeItem;", "isLoading", "snackbarMessage", "", "(ZLjava/util/List;Ljava/util/List;Ljava/util/List;ZLjava/lang/String;)V", "()Z", "getKnowledgeItems", "()Ljava/util/List;", "getRecentEscalations", "getRecentLogs", "getSnackbarMessage", "()Ljava/lang/String;", "component1", "component2", "component3", "component4", "component5", "component6", "copy", "equals", "other", "hashCode", "", "toString", "app_debug"})
public final class UiState {
    private final boolean isServiceEnabled = false;
    @org.jetbrains.annotations.NotNull()
    private final java.util.List<com.travlytic.app.data.db.entities.ResponseLog> recentLogs = null;
    @org.jetbrains.annotations.NotNull()
    private final java.util.List<com.travlytic.app.data.db.entities.EscalationLog> recentEscalations = null;
    @org.jetbrains.annotations.NotNull()
    private final java.util.List<com.travlytic.app.data.db.entities.KnowledgeItem> knowledgeItems = null;
    private final boolean isLoading = false;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String snackbarMessage = null;
    
    public UiState(boolean isServiceEnabled, @org.jetbrains.annotations.NotNull()
    java.util.List<com.travlytic.app.data.db.entities.ResponseLog> recentLogs, @org.jetbrains.annotations.NotNull()
    java.util.List<com.travlytic.app.data.db.entities.EscalationLog> recentEscalations, @org.jetbrains.annotations.NotNull()
    java.util.List<com.travlytic.app.data.db.entities.KnowledgeItem> knowledgeItems, boolean isLoading, @org.jetbrains.annotations.Nullable()
    java.lang.String snackbarMessage) {
        super();
    }
    
    public final boolean isServiceEnabled() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.travlytic.app.data.db.entities.ResponseLog> getRecentLogs() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.travlytic.app.data.db.entities.EscalationLog> getRecentEscalations() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.travlytic.app.data.db.entities.KnowledgeItem> getKnowledgeItems() {
        return null;
    }
    
    public final boolean isLoading() {
        return false;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getSnackbarMessage() {
        return null;
    }
    
    public UiState() {
        super();
    }
    
    public final boolean component1() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.travlytic.app.data.db.entities.ResponseLog> component2() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.travlytic.app.data.db.entities.EscalationLog> component3() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.travlytic.app.data.db.entities.KnowledgeItem> component4() {
        return null;
    }
    
    public final boolean component5() {
        return false;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component6() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.ui.viewmodel.UiState copy(boolean isServiceEnabled, @org.jetbrains.annotations.NotNull()
    java.util.List<com.travlytic.app.data.db.entities.ResponseLog> recentLogs, @org.jetbrains.annotations.NotNull()
    java.util.List<com.travlytic.app.data.db.entities.EscalationLog> recentEscalations, @org.jetbrains.annotations.NotNull()
    java.util.List<com.travlytic.app.data.db.entities.KnowledgeItem> knowledgeItems, boolean isLoading, @org.jetbrains.annotations.Nullable()
    java.lang.String snackbarMessage) {
        return null;
    }
    
    @java.lang.Override()
    public boolean equals(@org.jetbrains.annotations.Nullable()
    java.lang.Object other) {
        return false;
    }
    
    @java.lang.Override()
    public int hashCode() {
        return 0;
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.NotNull()
    public java.lang.String toString() {
        return null;
    }
}