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
import com.travlytic.app.data.db.entities.KnowledgeItem;
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
public final class KnowledgeItemDao_Impl implements KnowledgeItemDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<KnowledgeItem> __insertionAdapterOfKnowledgeItem;

  private final EntityDeletionOrUpdateAdapter<KnowledgeItem> __deletionAdapterOfKnowledgeItem;

  private final EntityDeletionOrUpdateAdapter<KnowledgeItem> __updateAdapterOfKnowledgeItem;

  private final SharedSQLiteStatement __preparedStmtOfDeleteAllExcelItems;

  public KnowledgeItemDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfKnowledgeItem = new EntityInsertionAdapter<KnowledgeItem>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `knowledge_items` (`id`,`type`,`reference`,`source`,`content`,`lastUpdated`,`isEnabled`) VALUES (nullif(?, 0),?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final KnowledgeItem entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getType() == null) {
          statement.bindNull(2);
        } else {
          statement.bindString(2, entity.getType());
        }
        if (entity.getReference() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getReference());
        }
        if (entity.getSource() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getSource());
        }
        if (entity.getContent() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getContent());
        }
        statement.bindLong(6, entity.getLastUpdated());
        final int _tmp = entity.isEnabled() ? 1 : 0;
        statement.bindLong(7, _tmp);
      }
    };
    this.__deletionAdapterOfKnowledgeItem = new EntityDeletionOrUpdateAdapter<KnowledgeItem>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "DELETE FROM `knowledge_items` WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final KnowledgeItem entity) {
        statement.bindLong(1, entity.getId());
      }
    };
    this.__updateAdapterOfKnowledgeItem = new EntityDeletionOrUpdateAdapter<KnowledgeItem>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `knowledge_items` SET `id` = ?,`type` = ?,`reference` = ?,`source` = ?,`content` = ?,`lastUpdated` = ?,`isEnabled` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final KnowledgeItem entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getType() == null) {
          statement.bindNull(2);
        } else {
          statement.bindString(2, entity.getType());
        }
        if (entity.getReference() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getReference());
        }
        if (entity.getSource() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getSource());
        }
        if (entity.getContent() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getContent());
        }
        statement.bindLong(6, entity.getLastUpdated());
        final int _tmp = entity.isEnabled() ? 1 : 0;
        statement.bindLong(7, _tmp);
        statement.bindLong(8, entity.getId());
      }
    };
    this.__preparedStmtOfDeleteAllExcelItems = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM knowledge_items WHERE type = 'excel'";
        return _query;
      }
    };
  }

  @Override
  public Object insert(final KnowledgeItem item, final Continuation<? super Long> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Long>() {
      @Override
      @NonNull
      public Long call() throws Exception {
        __db.beginTransaction();
        try {
          final Long _result = __insertionAdapterOfKnowledgeItem.insertAndReturnId(item);
          __db.setTransactionSuccessful();
          return _result;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object delete(final KnowledgeItem item, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __deletionAdapterOfKnowledgeItem.handle(item);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object update(final KnowledgeItem item, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfKnowledgeItem.handle(item);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteAllExcelItems(final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteAllExcelItems.acquire();
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
          __preparedStmtOfDeleteAllExcelItems.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<KnowledgeItem>> getAllFlow() {
    final String _sql = "SELECT * FROM knowledge_items";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"knowledge_items"}, new Callable<List<KnowledgeItem>>() {
      @Override
      @NonNull
      public List<KnowledgeItem> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfType = CursorUtil.getColumnIndexOrThrow(_cursor, "type");
          final int _cursorIndexOfReference = CursorUtil.getColumnIndexOrThrow(_cursor, "reference");
          final int _cursorIndexOfSource = CursorUtil.getColumnIndexOrThrow(_cursor, "source");
          final int _cursorIndexOfContent = CursorUtil.getColumnIndexOrThrow(_cursor, "content");
          final int _cursorIndexOfLastUpdated = CursorUtil.getColumnIndexOrThrow(_cursor, "lastUpdated");
          final int _cursorIndexOfIsEnabled = CursorUtil.getColumnIndexOrThrow(_cursor, "isEnabled");
          final List<KnowledgeItem> _result = new ArrayList<KnowledgeItem>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final KnowledgeItem _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpType;
            if (_cursor.isNull(_cursorIndexOfType)) {
              _tmpType = null;
            } else {
              _tmpType = _cursor.getString(_cursorIndexOfType);
            }
            final String _tmpReference;
            if (_cursor.isNull(_cursorIndexOfReference)) {
              _tmpReference = null;
            } else {
              _tmpReference = _cursor.getString(_cursorIndexOfReference);
            }
            final String _tmpSource;
            if (_cursor.isNull(_cursorIndexOfSource)) {
              _tmpSource = null;
            } else {
              _tmpSource = _cursor.getString(_cursorIndexOfSource);
            }
            final String _tmpContent;
            if (_cursor.isNull(_cursorIndexOfContent)) {
              _tmpContent = null;
            } else {
              _tmpContent = _cursor.getString(_cursorIndexOfContent);
            }
            final long _tmpLastUpdated;
            _tmpLastUpdated = _cursor.getLong(_cursorIndexOfLastUpdated);
            final boolean _tmpIsEnabled;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsEnabled);
            _tmpIsEnabled = _tmp != 0;
            _item = new KnowledgeItem(_tmpId,_tmpType,_tmpReference,_tmpSource,_tmpContent,_tmpLastUpdated,_tmpIsEnabled);
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
  public Object getEnabledItems(final Continuation<? super List<KnowledgeItem>> $completion) {
    final String _sql = "SELECT * FROM knowledge_items WHERE isEnabled = 1";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<KnowledgeItem>>() {
      @Override
      @NonNull
      public List<KnowledgeItem> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfType = CursorUtil.getColumnIndexOrThrow(_cursor, "type");
          final int _cursorIndexOfReference = CursorUtil.getColumnIndexOrThrow(_cursor, "reference");
          final int _cursorIndexOfSource = CursorUtil.getColumnIndexOrThrow(_cursor, "source");
          final int _cursorIndexOfContent = CursorUtil.getColumnIndexOrThrow(_cursor, "content");
          final int _cursorIndexOfLastUpdated = CursorUtil.getColumnIndexOrThrow(_cursor, "lastUpdated");
          final int _cursorIndexOfIsEnabled = CursorUtil.getColumnIndexOrThrow(_cursor, "isEnabled");
          final List<KnowledgeItem> _result = new ArrayList<KnowledgeItem>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final KnowledgeItem _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpType;
            if (_cursor.isNull(_cursorIndexOfType)) {
              _tmpType = null;
            } else {
              _tmpType = _cursor.getString(_cursorIndexOfType);
            }
            final String _tmpReference;
            if (_cursor.isNull(_cursorIndexOfReference)) {
              _tmpReference = null;
            } else {
              _tmpReference = _cursor.getString(_cursorIndexOfReference);
            }
            final String _tmpSource;
            if (_cursor.isNull(_cursorIndexOfSource)) {
              _tmpSource = null;
            } else {
              _tmpSource = _cursor.getString(_cursorIndexOfSource);
            }
            final String _tmpContent;
            if (_cursor.isNull(_cursorIndexOfContent)) {
              _tmpContent = null;
            } else {
              _tmpContent = _cursor.getString(_cursorIndexOfContent);
            }
            final long _tmpLastUpdated;
            _tmpLastUpdated = _cursor.getLong(_cursorIndexOfLastUpdated);
            final boolean _tmpIsEnabled;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsEnabled);
            _tmpIsEnabled = _tmp != 0;
            _item = new KnowledgeItem(_tmpId,_tmpType,_tmpReference,_tmpSource,_tmpContent,_tmpLastUpdated,_tmpIsEnabled);
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
  public Object getUrlItems(final Continuation<? super List<KnowledgeItem>> $completion) {
    final String _sql = "SELECT * FROM knowledge_items WHERE type = 'url'";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<KnowledgeItem>>() {
      @Override
      @NonNull
      public List<KnowledgeItem> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfType = CursorUtil.getColumnIndexOrThrow(_cursor, "type");
          final int _cursorIndexOfReference = CursorUtil.getColumnIndexOrThrow(_cursor, "reference");
          final int _cursorIndexOfSource = CursorUtil.getColumnIndexOrThrow(_cursor, "source");
          final int _cursorIndexOfContent = CursorUtil.getColumnIndexOrThrow(_cursor, "content");
          final int _cursorIndexOfLastUpdated = CursorUtil.getColumnIndexOrThrow(_cursor, "lastUpdated");
          final int _cursorIndexOfIsEnabled = CursorUtil.getColumnIndexOrThrow(_cursor, "isEnabled");
          final List<KnowledgeItem> _result = new ArrayList<KnowledgeItem>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final KnowledgeItem _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpType;
            if (_cursor.isNull(_cursorIndexOfType)) {
              _tmpType = null;
            } else {
              _tmpType = _cursor.getString(_cursorIndexOfType);
            }
            final String _tmpReference;
            if (_cursor.isNull(_cursorIndexOfReference)) {
              _tmpReference = null;
            } else {
              _tmpReference = _cursor.getString(_cursorIndexOfReference);
            }
            final String _tmpSource;
            if (_cursor.isNull(_cursorIndexOfSource)) {
              _tmpSource = null;
            } else {
              _tmpSource = _cursor.getString(_cursorIndexOfSource);
            }
            final String _tmpContent;
            if (_cursor.isNull(_cursorIndexOfContent)) {
              _tmpContent = null;
            } else {
              _tmpContent = _cursor.getString(_cursorIndexOfContent);
            }
            final long _tmpLastUpdated;
            _tmpLastUpdated = _cursor.getLong(_cursorIndexOfLastUpdated);
            final boolean _tmpIsEnabled;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsEnabled);
            _tmpIsEnabled = _tmp != 0;
            _item = new KnowledgeItem(_tmpId,_tmpType,_tmpReference,_tmpSource,_tmpContent,_tmpLastUpdated,_tmpIsEnabled);
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
