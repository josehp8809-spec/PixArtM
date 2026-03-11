package com.travlytic.app.data.db.dao;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0002\u0010 \n\u0002\b\u0003\n\u0002\u0010\t\n\u0002\b\u0002\bg\u0018\u00002\u00020\u0001J\u0016\u0010\u0002\u001a\u00020\u00032\u0006\u0010\u0004\u001a\u00020\u0005H\u00a7@\u00a2\u0006\u0002\u0010\u0006J\u000e\u0010\u0007\u001a\u00020\u0003H\u00a7@\u00a2\u0006\u0002\u0010\bJ\u0014\u0010\t\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00050\u000b0\nH\'J\u0014\u0010\f\u001a\b\u0012\u0004\u0012\u00020\u00050\u000bH\u00a7@\u00a2\u0006\u0002\u0010\bJ\u0014\u0010\r\u001a\b\u0012\u0004\u0012\u00020\u00050\u000bH\u00a7@\u00a2\u0006\u0002\u0010\bJ\u0016\u0010\u000e\u001a\u00020\u000f2\u0006\u0010\u0004\u001a\u00020\u0005H\u00a7@\u00a2\u0006\u0002\u0010\u0006J\u0016\u0010\u0010\u001a\u00020\u00032\u0006\u0010\u0004\u001a\u00020\u0005H\u00a7@\u00a2\u0006\u0002\u0010\u0006\u00a8\u0006\u0011"}, d2 = {"Lcom/travlytic/app/data/db/dao/KnowledgeItemDao;", "", "delete", "", "item", "Lcom/travlytic/app/data/db/entities/KnowledgeItem;", "(Lcom/travlytic/app/data/db/entities/KnowledgeItem;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "deleteAllExcelItems", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getAllFlow", "Lkotlinx/coroutines/flow/Flow;", "", "getEnabledItems", "getUrlItems", "insert", "", "update", "app_debug"})
@androidx.room.Dao()
public abstract interface KnowledgeItemDao {
    
    @androidx.room.Query(value = "SELECT * FROM knowledge_items")
    @org.jetbrains.annotations.NotNull()
    public abstract kotlinx.coroutines.flow.Flow<java.util.List<com.travlytic.app.data.db.entities.KnowledgeItem>> getAllFlow();
    
    @androidx.room.Query(value = "SELECT * FROM knowledge_items WHERE isEnabled = 1")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getEnabledItems(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.travlytic.app.data.db.entities.KnowledgeItem>> $completion);
    
    @androidx.room.Insert(onConflict = 1)
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object insert(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.KnowledgeItem item, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Long> $completion);
    
    @androidx.room.Update()
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object update(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.KnowledgeItem item, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @androidx.room.Delete()
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object delete(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.KnowledgeItem item, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM knowledge_items WHERE type = \'url\'")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getUrlItems(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.travlytic.app.data.db.entities.KnowledgeItem>> $completion);
    
    @androidx.room.Query(value = "DELETE FROM knowledge_items WHERE type = \'excel\'")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object deleteAllExcelItems(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
}