package com.travlytic.app.data.db.dao;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import com.travlytic.app.data.db.entities.ResponseLog;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Integer;
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
public final class ResponseLogDao_Impl implements ResponseLogDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<ResponseLog> __insertionAdapterOfResponseLog;

  private final SharedSQLiteStatement __preparedStmtOfDeleteAll;

  public ResponseLogDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfResponseLog = new EntityInsertionAdapter<ResponseLog>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `response_log` (`id`,`contact`,`incomingMessage`,`sentResponse`,`timestamp`,`sheetsUsed`) VALUES (nullif(?, 0),?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final ResponseLog entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getContact() == null) {
          statement.bindNull(2);
        } else {
          statement.bindString(2, entity.getContact());
        }
        if (entity.getIncomingMessage() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getIncomingMessage());
        }
        if (entity.getSentResponse() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getSentResponse());
        }
        statement.bindLong(5, entity.getTimestamp());
        if (entity.getSheetsUsed() == null) {
          statement.bindNull(6);
        } else {
          statement.bindString(6, entity.getSheetsUsed());
        }
      }
    };
    this.__preparedStmtOfDeleteAll = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM response_log";
        return _query;
      }
    };
  }

  @Override
  public Object insert(final ResponseLog log, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfResponseLog.insert(log);
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
  public Flow<List<ResponseLog>> observeRecent(final int limit) {
    final String _sql = "SELECT * FROM response_log ORDER BY timestamp DESC LIMIT ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, limit);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"response_log"}, new Callable<List<ResponseLog>>() {
      @Override
      @NonNull
      public List<ResponseLog> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfContact = CursorUtil.getColumnIndexOrThrow(_cursor, "contact");
          final int _cursorIndexOfIncomingMessage = CursorUtil.getColumnIndexOrThrow(_cursor, "incomingMessage");
          final int _cursorIndexOfSentResponse = CursorUtil.getColumnIndexOrThrow(_cursor, "sentResponse");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfSheetsUsed = CursorUtil.getColumnIndexOrThrow(_cursor, "sheetsUsed");
          final List<ResponseLog> _result = new ArrayList<ResponseLog>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final ResponseLog _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpContact;
            if (_cursor.isNull(_cursorIndexOfContact)) {
              _tmpContact = null;
            } else {
              _tmpContact = _cursor.getString(_cursorIndexOfContact);
            }
            final String _tmpIncomingMessage;
            if (_cursor.isNull(_cursorIndexOfIncomingMessage)) {
              _tmpIncomingMessage = null;
            } else {
              _tmpIncomingMessage = _cursor.getString(_cursorIndexOfIncomingMessage);
            }
            final String _tmpSentResponse;
            if (_cursor.isNull(_cursorIndexOfSentResponse)) {
              _tmpSentResponse = null;
            } else {
              _tmpSentResponse = _cursor.getString(_cursorIndexOfSentResponse);
            }
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            final String _tmpSheetsUsed;
            if (_cursor.isNull(_cursorIndexOfSheetsUsed)) {
              _tmpSheetsUsed = null;
            } else {
              _tmpSheetsUsed = _cursor.getString(_cursorIndexOfSheetsUsed);
            }
            _item = new ResponseLog(_tmpId,_tmpContact,_tmpIncomingMessage,_tmpSentResponse,_tmpTimestamp,_tmpSheetsUsed);
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
  public Object getRecent(final int limit,
      final Continuation<? super List<ResponseLog>> $completion) {
    final String _sql = "SELECT * FROM response_log ORDER BY timestamp DESC LIMIT ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, limit);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<ResponseLog>>() {
      @Override
      @NonNull
      public List<ResponseLog> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfContact = CursorUtil.getColumnIndexOrThrow(_cursor, "contact");
          final int _cursorIndexOfIncomingMessage = CursorUtil.getColumnIndexOrThrow(_cursor, "incomingMessage");
          final int _cursorIndexOfSentResponse = CursorUtil.getColumnIndexOrThrow(_cursor, "sentResponse");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfSheetsUsed = CursorUtil.getColumnIndexOrThrow(_cursor, "sheetsUsed");
          final List<ResponseLog> _result = new ArrayList<ResponseLog>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final ResponseLog _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpContact;
            if (_cursor.isNull(_cursorIndexOfContact)) {
              _tmpContact = null;
            } else {
              _tmpContact = _cursor.getString(_cursorIndexOfContact);
            }
            final String _tmpIncomingMessage;
            if (_cursor.isNull(_cursorIndexOfIncomingMessage)) {
              _tmpIncomingMessage = null;
            } else {
              _tmpIncomingMessage = _cursor.getString(_cursorIndexOfIncomingMessage);
            }
            final String _tmpSentResponse;
            if (_cursor.isNull(_cursorIndexOfSentResponse)) {
              _tmpSentResponse = null;
            } else {
              _tmpSentResponse = _cursor.getString(_cursorIndexOfSentResponse);
            }
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            final String _tmpSheetsUsed;
            if (_cursor.isNull(_cursorIndexOfSheetsUsed)) {
              _tmpSheetsUsed = null;
            } else {
              _tmpSheetsUsed = _cursor.getString(_cursorIndexOfSheetsUsed);
            }
            _item = new ResponseLog(_tmpId,_tmpContact,_tmpIncomingMessage,_tmpSentResponse,_tmpTimestamp,_tmpSheetsUsed);
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

  @Override
  public Object count(final Continuation<? super Integer> $completion) {
    final String _sql = "SELECT COUNT(*) FROM response_log";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<Integer>() {
      @Override
      @NonNull
      public Integer call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final Integer _result;
          if (_cursor.moveToFirst()) {
            final Integer _tmp;
            if (_cursor.isNull(0)) {
              _tmp = null;
            } else {
              _tmp = _cursor.getInt(0);
            }
            _result = _tmp;
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Object getLogCountForContact(final String contactName,
      final Continuation<? super Integer> $completion) {
    final String _sql = "SELECT COUNT(*) FROM response_log WHERE contact = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    if (contactName == null) {
      _statement.bindNull(_argIndex);
    } else {
      _statement.bindString(_argIndex, contactName);
    }
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<Integer>() {
      @Override
      @NonNull
      public Integer call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final Integer _result;
          if (_cursor.moveToFirst()) {
            final Integer _tmp;
            if (_cursor.isNull(0)) {
              _tmp = null;
            } else {
              _tmp = _cursor.getInt(0);
            }
            _result = _tmp;
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Object getRecentForContact(final String contactName, final int limit,
      final Continuation<? super List<ResponseLog>> $completion) {
    final String _sql = "SELECT * FROM response_log WHERE contact = ? ORDER BY timestamp DESC LIMIT ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 2);
    int _argIndex = 1;
    if (contactName == null) {
      _statement.bindNull(_argIndex);
    } else {
      _statement.bindString(_argIndex, contactName);
    }
    _argIndex = 2;
    _statement.bindLong(_argIndex, limit);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<ResponseLog>>() {
      @Override
      @NonNull
      public List<ResponseLog> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfContact = CursorUtil.getColumnIndexOrThrow(_cursor, "contact");
          final int _cursorIndexOfIncomingMessage = CursorUtil.getColumnIndexOrThrow(_cursor, "incomingMessage");
          final int _cursorIndexOfSentResponse = CursorUtil.getColumnIndexOrThrow(_cursor, "sentResponse");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfSheetsUsed = CursorUtil.getColumnIndexOrThrow(_cursor, "sheetsUsed");
          final List<ResponseLog> _result = new ArrayList<ResponseLog>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final ResponseLog _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpContact;
            if (_cursor.isNull(_cursorIndexOfContact)) {
              _tmpContact = null;
            } else {
              _tmpContact = _cursor.getString(_cursorIndexOfContact);
            }
            final String _tmpIncomingMessage;
            if (_cursor.isNull(_cursorIndexOfIncomingMessage)) {
              _tmpIncomingMessage = null;
            } else {
              _tmpIncomingMessage = _cursor.getString(_cursorIndexOfIncomingMessage);
            }
            final String _tmpSentResponse;
            if (_cursor.isNull(_cursorIndexOfSentResponse)) {
              _tmpSentResponse = null;
            } else {
              _tmpSentResponse = _cursor.getString(_cursorIndexOfSentResponse);
            }
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            final String _tmpSheetsUsed;
            if (_cursor.isNull(_cursorIndexOfSheetsUsed)) {
              _tmpSheetsUsed = null;
            } else {
              _tmpSheetsUsed = _cursor.getString(_cursorIndexOfSheetsUsed);
            }
            _item = new ResponseLog(_tmpId,_tmpContact,_tmpIncomingMessage,_tmpSentResponse,_tmpTimestamp,_tmpSheetsUsed);
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
