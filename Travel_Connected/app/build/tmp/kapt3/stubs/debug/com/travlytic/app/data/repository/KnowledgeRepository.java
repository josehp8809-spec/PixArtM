package com.travlytic.app.data.repository;

@javax.inject.Singleton()
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000H\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0002\n\u0002\b\u0005\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0004\n\u0002\u0010\u000b\n\u0002\b\u0002\b\u0007\u0018\u00002\u00020\u0001B\u0019\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\b\b\u0001\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\u0002\u0010\u0006J\u000e\u0010\r\u001a\u00020\u000eH\u0086@\u00a2\u0006\u0002\u0010\u000fJ\u0016\u0010\u0010\u001a\u00020\u000e2\u0006\u0010\u0011\u001a\u00020\nH\u0086@\u00a2\u0006\u0002\u0010\u0012J\u000e\u0010\u0013\u001a\u00020\u0014H\u0086@\u00a2\u0006\u0002\u0010\u000fJ\u001e\u0010\u0015\u001a\u00020\u000e2\u0006\u0010\u0016\u001a\u00020\u00172\u0006\u0010\u0018\u001a\u00020\u0014H\u0086@\u00a2\u0006\u0002\u0010\u0019J\u001e\u0010\u001a\u001a\u00020\u000e2\u0006\u0010\u0011\u001a\u00020\n2\u0006\u0010\u001b\u001a\u00020\u001cH\u0086@\u00a2\u0006\u0002\u0010\u001dR\u000e\u0010\u0004\u001a\u00020\u0005X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u001d\u0010\u0007\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\n0\t0\b\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000b\u0010\f\u00a8\u0006\u001e"}, d2 = {"Lcom/travlytic/app/data/repository/KnowledgeRepository;", "", "dao", "Lcom/travlytic/app/data/db/dao/KnowledgeItemDao;", "context", "Landroid/content/Context;", "(Lcom/travlytic/app/data/db/dao/KnowledgeItemDao;Landroid/content/Context;)V", "knowledgeItemsFlow", "Lkotlinx/coroutines/flow/Flow;", "", "Lcom/travlytic/app/data/db/entities/KnowledgeItem;", "getKnowledgeItemsFlow", "()Lkotlinx/coroutines/flow/Flow;", "deleteAllExcelItems", "", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "deleteItem", "item", "(Lcom/travlytic/app/data/db/entities/KnowledgeItem;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getEnabledContextString", "", "importExcel", "uri", "Landroid/net/Uri;", "reference", "(Landroid/net/Uri;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "toggleItem", "enabled", "", "(Lcom/travlytic/app/data/db/entities/KnowledgeItem;ZLkotlin/coroutines/Continuation;)Ljava/lang/Object;", "app_debug"})
public final class KnowledgeRepository {
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.data.db.dao.KnowledgeItemDao dao = null;
    @org.jetbrains.annotations.NotNull()
    private final android.content.Context context = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.Flow<java.util.List<com.travlytic.app.data.db.entities.KnowledgeItem>> knowledgeItemsFlow = null;
    
    @javax.inject.Inject()
    public KnowledgeRepository(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.dao.KnowledgeItemDao dao, @dagger.hilt.android.qualifiers.ApplicationContext()
    @org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.Flow<java.util.List<com.travlytic.app.data.db.entities.KnowledgeItem>> getKnowledgeItemsFlow() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object getEnabledContextString(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.String> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object importExcel(@org.jetbrains.annotations.NotNull()
    android.net.Uri uri, @org.jetbrains.annotations.NotNull()
    java.lang.String reference, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object toggleItem(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.KnowledgeItem item, boolean enabled, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object deleteItem(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.KnowledgeItem item, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object deleteAllExcelItems(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion) {
        return null;
    }
}