package com.travlytic.app.data.db.dao;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00004\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\b\n\u0002\u0018\u0002\n\u0000\bg\u0018\u00002\u00020\u0001J\u000e\u0010\u0002\u001a\u00020\u0003H\u00a7@\u00a2\u0006\u0002\u0010\u0004J\u000e\u0010\u0005\u001a\u00020\u0006H\u00a7@\u00a2\u0006\u0002\u0010\u0004J\u0016\u0010\u0007\u001a\u00020\u00032\u0006\u0010\b\u001a\u00020\tH\u00a7@\u00a2\u0006\u0002\u0010\nJ\u001e\u0010\u000b\u001a\b\u0012\u0004\u0012\u00020\r0\f2\b\b\u0002\u0010\u000e\u001a\u00020\u0003H\u00a7@\u00a2\u0006\u0002\u0010\u000fJ&\u0010\u0010\u001a\b\u0012\u0004\u0012\u00020\r0\f2\u0006\u0010\b\u001a\u00020\t2\b\b\u0002\u0010\u000e\u001a\u00020\u0003H\u00a7@\u00a2\u0006\u0002\u0010\u0011J\u0016\u0010\u0012\u001a\u00020\u00062\u0006\u0010\u0013\u001a\u00020\rH\u00a7@\u00a2\u0006\u0002\u0010\u0014J\u001e\u0010\u0015\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\r0\f0\u00162\b\b\u0002\u0010\u000e\u001a\u00020\u0003H\'\u00a8\u0006\u0017"}, d2 = {"Lcom/travlytic/app/data/db/dao/ResponseLogDao;", "", "count", "", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "deleteAll", "", "getLogCountForContact", "contactName", "", "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getRecent", "", "Lcom/travlytic/app/data/db/entities/ResponseLog;", "limit", "(ILkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getRecentForContact", "(Ljava/lang/String;ILkotlin/coroutines/Continuation;)Ljava/lang/Object;", "insert", "log", "(Lcom/travlytic/app/data/db/entities/ResponseLog;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "observeRecent", "Lkotlinx/coroutines/flow/Flow;", "app_debug"})
@androidx.room.Dao()
public abstract interface ResponseLogDao {
    
    @androidx.room.Query(value = "SELECT * FROM response_log ORDER BY timestamp DESC LIMIT :limit")
    @org.jetbrains.annotations.NotNull()
    public abstract kotlinx.coroutines.flow.Flow<java.util.List<com.travlytic.app.data.db.entities.ResponseLog>> observeRecent(int limit);
    
    @androidx.room.Query(value = "SELECT * FROM response_log ORDER BY timestamp DESC LIMIT :limit")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getRecent(int limit, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.travlytic.app.data.db.entities.ResponseLog>> $completion);
    
    @androidx.room.Insert(onConflict = 1)
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object insert(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.ResponseLog log, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @androidx.room.Query(value = "DELETE FROM response_log")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object deleteAll(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @androidx.room.Query(value = "SELECT COUNT(*) FROM response_log")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object count(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Integer> $completion);
    
    @androidx.room.Query(value = "SELECT COUNT(*) FROM response_log WHERE contact = :contactName")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getLogCountForContact(@org.jetbrains.annotations.NotNull()
    java.lang.String contactName, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Integer> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM response_log WHERE contact = :contactName ORDER BY timestamp DESC LIMIT :limit")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getRecentForContact(@org.jetbrains.annotations.NotNull()
    java.lang.String contactName, int limit, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.travlytic.app.data.db.entities.ResponseLog>> $completion);
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 3, xi = 48)
    public static final class DefaultImpls {
    }
}