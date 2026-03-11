package com.travlytic.app.data.db.dao;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityDeletionOrUpdateAdapter;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import com.travlytic.app.data.db.entities.TrainingRule;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Object;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import javax.annotation.processing.Generated;
import kotlin.Unit;
import kotlin.coroutines.Continuation;
import kotlinx.coroutines.flow.Flow;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class TrainingRuleDao_Impl implements TrainingRuleDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<TrainingRule> __insertionAdapterOfTrainingRule;

  private final EntityDeletionOrUpdateAdapter<TrainingRule> __deletionAdapterOfTrainingRule;

  private final EntityDeletionOrUpdateAdapter<TrainingRule> __updateAdapterOfTrainingRule;

  private final SharedSQLiteStatement __preparedStmtOfDeleteAll;

  public TrainingRuleDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfTrainingRule = new EntityInsertionAdapter<TrainingRule>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `training_rules` (`id`,`type`,`input`,`output`,`isActive`) VALUES (nullif(?, 0),?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final TrainingRule entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getType() == null) {
          statement.bindNull(2);
        } else {
          statement.bindString(2, entity.getType());
        }
        if (entity.getInput() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getInput());
        }
        if (entity.getOutput() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getOutput());
        }
        final int _tmp = entity.isActive() ? 1 : 0;
        statement.bindLong(5, _tmp);
      }
    };
    this.__deletionAdapterOfTrainingRule = new EntityDeletionOrUpdateAdapter<TrainingRule>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "DELETE FROM `training_rules` WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final TrainingRule entity) {
        statement.bindLong(1, entity.getId());
      }
    };
    this.__updateAdapterOfTrainingRule = new EntityDeletionOrUpdateAdapter<TrainingRule>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `training_rules` SET `id` = ?,`type` = ?,`input` = ?,`output` = ?,`isActive` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final TrainingRule entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getType() == null) {
          statement.bindNull(2);
        } else {
          statement.bindString(2, entity.getType());
        }
        if (entity.getInput() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getInput());
        }
        if (entity.getOutput() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getOutput());
        }
        final int _tmp = entity.isActive() ? 1 : 0;
        statement.bindLong(5, _tmp);
        statement.bindLong(6, entity.getId());
      }
    };
    this.__preparedStmtOfDeleteAll = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM training_rules";
        return _query;
      }
    };
  }

  @Override
  public Object insert(final TrainingRule rule, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfTrainingRule.insert(rule);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertAll(final List<TrainingRule> rules,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfTrainingRule.insert(rules);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object delete(final TrainingRule rule, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __deletionAdapterOfTrainingRule.handle(rule);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object update(final TrainingRule rule, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfTrainingRule.handle(rule);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteAll(final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteAll.acquire();
        try {
          __db.beginTransaction();
          try {
            _stmt.executeUpdateDelete();
            __db.setTransactionSuccessful();
            return Unit.INSTANCE;
          } finally {
            __db.endTransaction();
          }
        } finally {
          __preparedStmtOfDeleteAll.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<TrainingRule>> observeAll() {
    final String _sql = "SELECT * FROM training_rules ORDER BY type ASC, id DESC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"training_rules"}, new Callable<List<TrainingRule>>() {
      @Override
      @NonNull
      public List<TrainingRule> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfType = CursorUtil.getColumnIndexOrThrow(_cursor, "type");
          final int _cursorIndexOfInput = CursorUtil.getColumnIndexOrThrow(_cursor, "input");
          final int _cursorIndexOfOutput = CursorUtil.getColumnIndexOrThrow(_cursor, "output");
          final int _cursorIndexOfIsActive = CursorUtil.getColumnIndexOrThrow(_cursor, "isActive");
          final List<TrainingRule> _result = new ArrayList<TrainingRule>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final TrainingRule _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpType;
            if (_cursor.isNull(_cursorIndexOfType)) {
              _tmpType = null;
            } else {
              _tmpType = _cursor.getString(_cursorIndexOfType);
            }
            final String _tmpInput;
            if (_cursor.isNull(_cursorIndexOfInput)) {
              _tmpInput = null;
            } else {
              _tmpInput = _cursor.getString(_cursorIndexOfInput);
            }
            final String _tmpOutput;
            if (_cursor.isNull(_cursorIndexOfOutput)) {
              _tmpOutput = null;
            } else {
              _tmpOutput = _cursor.getString(_cursorIndexOfOutput);
            }
            final boolean _tmpIsActive;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsActive);
            _tmpIsActive = _tmp != 0;
            _item = new TrainingRule(_tmpId,_tmpType,_tmpInput,_tmpOutput,_tmpIsActive);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @Override
  public Object getActiveRules(final Continuation<? super List<TrainingRule>> $completion) {
    final String _sql = "SELECT * FROM training_rules WHERE isActive = 1 ORDER BY type ASC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<TrainingRule>>() {
      @Override
      @NonNull
      public List<TrainingRule> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfType = CursorUtil.getColumnIndexOrThrow(_cursor, "type");
          final int _cursorIndexOfInput = CursorUtil.getColumnIndexOrThrow(_cursor, "input");
          final int _cursorIndexOfOutput = CursorUtil.getColumnIndexOrThrow(_cursor, "output");
          final int _cursorIndexOfIsActive = CursorUtil.getColumnIndexOrThrow(_cursor, "isActive");
          final List<TrainingRule> _result = new ArrayList<TrainingRule>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final TrainingRule _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpType;
            if (_cursor.isNull(_cursorIndexOfType)) {
              _tmpType = null;
            } else {
              _tmpType = _cursor.getString(_cursorIndexOfType);
            }
            final String _tmpInput;
            if (_cursor.isNull(_cursorIndexOfInput)) {
              _tmpInput = null;
            } else {
              _tmpInput = _cursor.getString(_cursorIndexOfInput);
            }
            final String _tmpOutput;
            if (_cursor.isNull(_cursorIndexOfOutput)) {
              _tmpOutput = null;
            } else {
              _tmpOutput = _cursor.getString(_cursorIndexOfOutput);
            }
            final boolean _tmpIsActive;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsActive);
            _tmpIsActive = _tmp != 0;
            _item = new TrainingRule(_tmpId,_tmpType,_tmpInput,_tmpOutput,_tmpIsActive);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
