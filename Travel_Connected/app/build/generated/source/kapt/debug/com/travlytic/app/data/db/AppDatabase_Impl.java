package com.travlytic.app.data.db;

import androidx.annotation.NonNull;
import androidx.room.DatabaseConfiguration;
import androidx.room.InvalidationTracker;
import androidx.room.RoomDatabase;
import androidx.room.RoomOpenHelper;
import androidx.room.migration.AutoMigrationSpec;
import androidx.room.migration.Migration;
import androidx.room.util.DBUtil;
import androidx.room.util.TableInfo;
import androidx.sqlite.db.SupportSQLiteDatabase;
import androidx.sqlite.db.SupportSQLiteOpenHelper;
import com.travlytic.app.data.db.dao.EscalationLogDao;
import com.travlytic.app.data.db.dao.EscalationLogDao_Impl;
import com.travlytic.app.data.db.dao.KnowledgeItemDao;
import com.travlytic.app.data.db.dao.KnowledgeItemDao_Impl;
import com.travlytic.app.data.db.dao.ResponseLogDao;
import com.travlytic.app.data.db.dao.ResponseLogDao_Impl;
import com.travlytic.app.data.db.dao.TrainingRuleDao;
import com.travlytic.app.data.db.dao.TrainingRuleDao_Impl;
import java.lang.Class;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.annotation.processing.Generated;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class AppDatabase_Impl extends AppDatabase {
  private volatile KnowledgeItemDao _knowledgeItemDao;

  private volatile EscalationLogDao _escalationLogDao;

  private volatile ResponseLogDao _responseLogDao;

  private volatile TrainingRuleDao _trainingRuleDao;

  @Override
  @NonNull
  protected SupportSQLiteOpenHelper createOpenHelper(@NonNull final DatabaseConfiguration config) {
    final SupportSQLiteOpenHelper.Callback _openCallback = new RoomOpenHelper(config, new RoomOpenHelper.Delegate(3) {
      @Override
      public void createAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("CREATE TABLE IF NOT EXISTS `knowledge_items` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `type` TEXT NOT NULL, `reference` TEXT NOT NULL, `source` TEXT NOT NULL, `content` TEXT NOT NULL, `lastUpdated` INTEGER NOT NULL, `isEnabled` INTEGER NOT NULL)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `escalation_logs` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `contact` TEXT NOT NULL, `originalMessage` TEXT NOT NULL, `timestamp` INTEGER NOT NULL, `isResolved` INTEGER NOT NULL)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `response_log` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `contact` TEXT NOT NULL, `incomingMessage` TEXT NOT NULL, `sentResponse` TEXT NOT NULL, `timestamp` INTEGER NOT NULL, `sheetsUsed` TEXT NOT NULL)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `training_rules` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `type` TEXT NOT NULL, `input` TEXT NOT NULL, `output` TEXT, `isActive` INTEGER NOT NULL)");
        db.execSQL("CREATE TABLE IF NOT EXISTS room_master_table (id INTEGER PRIMARY KEY,identity_hash TEXT)");
        db.execSQL("INSERT OR REPLACE INTO room_master_table (id,identity_hash) VALUES(42, '76a59770fe25accccb1a542b36956a99')");
      }

      @Override
      public void dropAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("DROP TABLE IF EXISTS `knowledge_items`");
        db.execSQL("DROP TABLE IF EXISTS `escalation_logs`");
        db.execSQL("DROP TABLE IF EXISTS `response_log`");
        db.execSQL("DROP TABLE IF EXISTS `training_rules`");
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onDestructiveMigration(db);
          }
        }
      }

      @Override
      public void onCreate(@NonNull final SupportSQLiteDatabase db) {
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onCreate(db);
          }
        }
      }

      @Override
      public void onOpen(@NonNull final SupportSQLiteDatabase db) {
        mDatabase = db;
        internalInitInvalidationTracker(db);
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onOpen(db);
          }
        }
      }

      @Override
      public void onPreMigrate(@NonNull final SupportSQLiteDatabase db) {
        DBUtil.dropFtsSyncTriggers(db);
      }

      @Override
      public void onPostMigrate(@NonNull final SupportSQLiteDatabase db) {
      }

      @Override
      @NonNull
      public RoomOpenHelper.ValidationResult onValidateSchema(
          @NonNull final SupportSQLiteDatabase db) {
        final HashMap<String, TableInfo.Column> _columnsKnowledgeItems = new HashMap<String, TableInfo.Column>(7);
        _columnsKnowledgeItems.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsKnowledgeItems.put("type", new TableInfo.Column("type", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsKnowledgeItems.put("reference", new TableInfo.Column("reference", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsKnowledgeItems.put("source", new TableInfo.Column("source", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsKnowledgeItems.put("content", new TableInfo.Column("content", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsKnowledgeItems.put("lastUpdated", new TableInfo.Column("lastUpdated", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsKnowledgeItems.put("isEnabled", new TableInfo.Column("isEnabled", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysKnowledgeItems = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesKnowledgeItems = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoKnowledgeItems = new TableInfo("knowledge_items", _columnsKnowledgeItems, _foreignKeysKnowledgeItems, _indicesKnowledgeItems);
        final TableInfo _existingKnowledgeItems = TableInfo.read(db, "knowledge_items");
        if (!_infoKnowledgeItems.equals(_existingKnowledgeItems)) {
          return new RoomOpenHelper.ValidationResult(false, "knowledge_items(com.travlytic.app.data.db.entities.KnowledgeItem).\n"
                  + " Expected:\n" + _infoKnowledgeItems + "\n"
                  + " Found:\n" + _existingKnowledgeItems);
        }
        final HashMap<String, TableInfo.Column> _columnsEscalationLogs = new HashMap<String, TableInfo.Column>(5);
        _columnsEscalationLogs.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEscalationLogs.put("contact", new TableInfo.Column("contact", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEscalationLogs.put("originalMessage", new TableInfo.Column("originalMessage", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEscalationLogs.put("timestamp", new TableInfo.Column("timestamp", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsEscalationLogs.put("isResolved", new TableInfo.Column("isResolved", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysEscalationLogs = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesEscalationLogs = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoEscalationLogs = new TableInfo("escalation_logs", _columnsEscalationLogs, _foreignKeysEscalationLogs, _indicesEscalationLogs);
        final TableInfo _existingEscalationLogs = TableInfo.read(db, "escalation_logs");
        if (!_infoEscalationLogs.equals(_existingEscalationLogs)) {
          return new RoomOpenHelper.ValidationResult(false, "escalation_logs(com.travlytic.app.data.db.entities.EscalationLog).\n"
                  + " Expected:\n" + _infoEscalationLogs + "\n"
                  + " Found:\n" + _existingEscalationLogs);
        }
        final HashMap<String, TableInfo.Column> _columnsResponseLog = new HashMap<String, TableInfo.Column>(6);
        _columnsResponseLog.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsResponseLog.put("contact", new TableInfo.Column("contact", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsResponseLog.put("incomingMessage", new TableInfo.Column("incomingMessage", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsResponseLog.put("sentResponse", new TableInfo.Column("sentResponse", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsResponseLog.put("timestamp", new TableInfo.Column("timestamp", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsResponseLog.put("sheetsUsed", new TableInfo.Column("sheetsUsed", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysResponseLog = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesResponseLog = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoResponseLog = new TableInfo("response_log", _columnsResponseLog, _foreignKeysResponseLog, _indicesResponseLog);
        final TableInfo _existingResponseLog = TableInfo.read(db, "response_log");
        if (!_infoResponseLog.equals(_existingResponseLog)) {
          return new RoomOpenHelper.ValidationResult(false, "response_log(com.travlytic.app.data.db.entities.ResponseLog).\n"
                  + " Expected:\n" + _infoResponseLog + "\n"
                  + " Found:\n" + _existingResponseLog);
        }
        final HashMap<String, TableInfo.Column> _columnsTrainingRules = new HashMap<String, TableInfo.Column>(5);
        _columnsTrainingRules.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRules.put("type", new TableInfo.Column("type", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRules.put("input", new TableInfo.Column("input", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRules.put("output", new TableInfo.Column("output", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRules.put("isActive", new TableInfo.Column("isActive", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysTrainingRules = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesTrainingRules = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoTrainingRules = new TableInfo("training_rules", _columnsTrainingRules, _foreignKeysTrainingRules, _indicesTrainingRules);
        final TableInfo _existingTrainingRules = TableInfo.read(db, "training_rules");
        if (!_infoTrainingRules.equals(_existingTrainingRules)) {
          return new RoomOpenHelper.ValidationResult(false, "training_rules(com.travlytic.app.data.db.entities.TrainingRule).\n"
                  + " Expected:\n" + _infoTrainingRules + "\n"
                  + " Found:\n" + _existingTrainingRules);
        }
        return new RoomOpenHelper.ValidationResult(true, null);
      }
    }, "76a59770fe25accccb1a542b36956a99", "fff3789b1898c99b10c4a7904c254c19");
    final SupportSQLiteOpenHelper.Configuration _sqliteConfig = SupportSQLiteOpenHelper.Configuration.builder(config.context).name(config.name).callback(_openCallback).build();
    final SupportSQLiteOpenHelper _helper = config.sqliteOpenHelperFactory.create(_sqliteConfig);
    return _helper;
  }

  @Override
  @NonNull
  protected InvalidationTracker createInvalidationTracker() {
    final HashMap<String, String> _shadowTablesMap = new HashMap<String, String>(0);
    final HashMap<String, Set<String>> _viewTables = new HashMap<String, Set<String>>(0);
    return new InvalidationTracker(this, _shadowTablesMap, _viewTables, "knowledge_items","escalation_logs","response_log","training_rules");
  }

  @Override
  public void clearAllTables() {
    super.assertNotMainThread();
    final SupportSQLiteDatabase _db = super.getOpenHelper().getWritableDatabase();
    try {
      super.beginTransaction();
      _db.execSQL("DELETE FROM `knowledge_items`");
      _db.execSQL("DELETE FROM `escalation_logs`");
      _db.execSQL("DELETE FROM `response_log`");
      _db.execSQL("DELETE FROM `training_rules`");
      super.setTransactionSuccessful();
    } finally {
      super.endTransaction();
      _db.query("PRAGMA wal_checkpoint(FULL)").close();
      if (!_db.inTransaction()) {
        _db.execSQL("VACUUM");
      }
    }
  }

  @Override
  @NonNull
  protected Map<Class<?>, List<Class<?>>> getRequiredTypeConverters() {
    final HashMap<Class<?>, List<Class<?>>> _typeConvertersMap = new HashMap<Class<?>, List<Class<?>>>();
    _typeConvertersMap.put(KnowledgeItemDao.class, KnowledgeItemDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(EscalationLogDao.class, EscalationLogDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(ResponseLogDao.class, ResponseLogDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(TrainingRuleDao.class, TrainingRuleDao_Impl.getRequiredConverters());
    return _typeConvertersMap;
  }

  @Override
  @NonNull
  public Set<Class<? extends AutoMigrationSpec>> getRequiredAutoMigrationSpecs() {
    final HashSet<Class<? extends AutoMigrationSpec>> _autoMigrationSpecsSet = new HashSet<Class<? extends AutoMigrationSpec>>();
    return _autoMigrationSpecsSet;
  }

  @Override
  @NonNull
  public List<Migration> getAutoMigrations(
      @NonNull final Map<Class<? extends AutoMigrationSpec>, AutoMigrationSpec> autoMigrationSpecs) {
    final List<Migration> _autoMigrations = new ArrayList<Migration>();
    return _autoMigrations;
  }

  @Override
  public KnowledgeItemDao knowledgeItemDao() {
    if (_knowledgeItemDao != null) {
      return _knowledgeItemDao;
    } else {
      synchronized(this) {
        if(_knowledgeItemDao == null) {
          _knowledgeItemDao = new KnowledgeItemDao_Impl(this);
        }
        return _knowledgeItemDao;
      }
    }
  }

  @Override
  public EscalationLogDao escalationLogDao() {
    if (_escalationLogDao != null) {
      return _escalationLogDao;
    } else {
      synchronized(this) {
        if(_escalationLogDao == null) {
          _escalationLogDao = new EscalationLogDao_Impl(this);
        }
        return _escalationLogDao;
      }
    }
  }

  @Override
  public ResponseLogDao responseLogDao() {
    if (_responseLogDao != null) {
      return _responseLogDao;
    } else {
      synchronized(this) {
        if(_responseLogDao == null) {
          _responseLogDao = new ResponseLogDao_Impl(this);
        }
        return _responseLogDao;
      }
    }
  }

  @Override
  public TrainingRuleDao trainingRuleDao() {
    if (_trainingRuleDao != null) {
      return _trainingRuleDao;
    } else {
      synchronized(this) {
        if(_trainingRuleDao == null) {
          _trainingRuleDao = new TrainingRuleDao_Impl(this);
        }
        return _trainingRuleDao;
      }
    }
  }
}
