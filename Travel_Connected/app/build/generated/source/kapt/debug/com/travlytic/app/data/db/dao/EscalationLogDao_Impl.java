package com.travlytic.app.data.db.dao;

import android.database.Cursor;
import androidx.annotation.NonNull;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityDeletionOrUpdateAdapter;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import com.travlytic.app.data.db.entities.EscalationLog;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Long;
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
public final class EscalationLogDao_Impl implements EscalationLogDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<EscalationLog> __insertionAdapterOfEscalationLog;

  private final EntityDeletionOrUpdateAdapter<EscalationLog> __deletionAdapterOfEscalationLog;

  private final EntityDeletionOrUpdateAdapter<EscalationLog> __updateAdapterOfEscalationLog;

  public EscalationLogDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfEscalationLog = new EntityInsertionAdapter<EscalationLog>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `escalation_logs` (`id`,`contact`,`originalMessage`,`timestamp`,`isResolved`) VALUES (nullif(?, 0),?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final EscalationLog entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getContact() == null) {
          statement.bindNull(2);
        } else {
          statement.bindString(2, entity.getContact());
        }
        if (entity.getOriginalMessage() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getOriginalMessage());
        }
        statement.bindLong(4, entity.getTimestamp());
        final int _tmp = entity.isResolved() ? 1 : 0;
        statement.bindLong(5, _tmp);
      }
    };
    this.__deletionAdapterOfEscalationLog = new EntityDeletionOrUpdateAdapter<EscalationLog>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "DELETE FROM `escalation_logs` WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final EscalationLog entity) {
        statement.bindLong(1, entity.getId());
      }
    };
    this.__updateAdapterOfEscalationLog = new EntityDeletionOrUpdateAdapter<EscalationLog>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `escalation_logs` SET `id` = ?,`contact` = ?,`originalMessage` = ?,`timestamp` = ?,`isResolved` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final EscalationLog entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getContact() == null) {
          statement.bindNull(2);
        } else {
          statement.bindString(2, entity.getContact());
        }
        if (entity.getOriginalMessage() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getOriginalMessage());
        }
        statement.bindLong(4, entity.getTimestamp());
        final int _tmp = entity.isResolved() ? 1 : 0;
        statement.bindLong(5, _tmp);
        statement.bindLong(6, entity.getId());
      }
    };
  }

  @Override
  public Object insert(final EscalationLog log, final Continuation<? super Long> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Long>() {
      @Override
      @NonNull
      public Long call() throws Exception {
        __db.beginTransaction();
        try {
          final Long _result = __insertionAdapterOfEscalationLog.insertAndReturnId(log);
          __db.setTransactionSuccessful();
          return _result;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object delete(final EscalationLog log, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __deletionAdapterOfEscalationLog.handle(log);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object update(final EscalationLog log, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfEscalationLog.handle(log);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<EscalationLog>> getAllFlow() {
    final String _sql = "SELECT * FROM escalation_logs ORDER BY timestamp DESC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"escalation_logs"}, new Callable<List<EscalationLog>>() {
      @Override
      @NonNull
      public List<EscalationLog> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfContact = CursorUtil.getColumnIndexOrThrow(_cursor, "contact");
          final int _cursorIndexOfOriginalMessage = CursorUtil.getColumnIndexOrThrow(_cursor, "originalMessage");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfIsResolved = CursorUtil.getColumnIndexOrThrow(_cursor, "isResolved");
          final List<EscalationLog> _result = new ArrayList<EscalationLog>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final EscalationLog _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpContact;
            if (_cursor.isNull(_cursorIndexOfContact)) {
              _tmpContact = null;
            } else {
              _tmpContact = _cursor.getString(_cursorIndexOfContact);
            }
            final String _tmpOriginalMessage;
            if (_cursor.isNull(_cursorIndexOfOriginalMessage)) {
              _tmpOriginalMessage = null;
            } else {
              _tmpOriginalMessage = _cursor.getString(_cursorIndexOfOriginalMessage);
            }
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            final boolean _tmpIsResolved;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsResolved);
            _tmpIsResolved = _tmp != 0;
            _item = new EscalationLog(_tmpId,_tmpContact,_tmpOriginalMessage,_tmpTimestamp,_tmpIsResolved);
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
  public Flow<List<EscalationLog>> getPendingFlow() {
    final String _sql = "SELECT * FROM escalation_logs WHERE isResolved = 0 ORDER BY timestamp DESC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"escalation_logs"}, new Callable<List<EscalationLog>>() {
      @Override
      @NonNull
      public List<EscalationLog> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfContact = CursorUtil.getColumnIndexOrThrow(_cursor, "contact");
          final int _cursorIndexOfOriginalMessage = CursorUtil.getColumnIndexOrThrow(_cursor, "originalMessage");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfIsResolved = CursorUtil.getColumnIndexOrThrow(_cursor, "isResolved");
          final List<EscalationLog> _result = new ArrayList<EscalationLog>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final EscalationLog _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpContact;
            if (_cursor.isNull(_cursorIndexOfContact)) {
              _tmpContact = null;
            } else {
              _tmpContact = _cursor.getString(_cursorIndexOfContact);
            }
            final String _tmpOriginalMessage;
            if (_cursor.isNull(_cursorIndexOfOriginalMessage)) {
              _tmpOriginalMessage = null;
            } else {
              _tmpOriginalMessage = _cursor.getString(_cursorIndexOfOriginalMessage);
            }
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            final boolean _tmpIsResolved;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsResolved);
            _tmpIsResolved = _tmp != 0;
            _item = new EscalationLog(_tmpId,_tmpContact,_tmpOriginalMessage,_tmpTimestamp,_tmpIsResolved);
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

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
