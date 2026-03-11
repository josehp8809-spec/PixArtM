package com.travlytic.app.data.db;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000$\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\b\'\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\b\u0010\u0003\u001a\u00020\u0004H&J\b\u0010\u0005\u001a\u00020\u0006H&J\b\u0010\u0007\u001a\u00020\bH&J\b\u0010\t\u001a\u00020\nH&\u00a8\u0006\u000b"}, d2 = {"Lcom/travlytic/app/data/db/AppDatabase;", "Landroidx/room/RoomDatabase;", "()V", "escalationLogDao", "Lcom/travlytic/app/data/db/dao/EscalationLogDao;", "knowledgeItemDao", "Lcom/travlytic/app/data/db/dao/KnowledgeItemDao;", "responseLogDao", "Lcom/travlytic/app/data/db/dao/ResponseLogDao;", "trainingRuleDao", "Lcom/travlytic/app/data/db/dao/TrainingRuleDao;", "app_debug"})
@androidx.room.Database(entities = {com.travlytic.app.data.db.entities.KnowledgeItem.class, com.travlytic.app.data.db.entities.EscalationLog.class, com.travlytic.app.data.db.entities.ResponseLog.class, com.travlytic.app.data.db.entities.TrainingRule.class}, version = 3, exportSchema = false)
public abstract class AppDatabase extends androidx.room.RoomDatabase {
    
    public AppDatabase() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public abstract com.travlytic.app.data.db.dao.KnowledgeItemDao knowledgeItemDao();
    
    @org.jetbrains.annotations.NotNull()
    public abstract com.travlytic.app.data.db.dao.EscalationLogDao escalationLogDao();
    
    @org.jetbrains.annotations.NotNull()
    public abstract com.travlytic.app.data.db.dao.ResponseLogDao responseLogDao();
    
    @org.jetbrains.annotations.NotNull()
    public abstract com.travlytic.app.data.db.dao.TrainingRuleDao trainingRuleDao();
}