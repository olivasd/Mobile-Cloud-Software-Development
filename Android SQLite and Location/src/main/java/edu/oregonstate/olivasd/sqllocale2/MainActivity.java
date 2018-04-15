package edu.oregonstate.olivasd.sqllocale2;

import android.Manifest;
import android.app.Dialog;
import android.content.ContentValues;
import android.content.Context;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.location.Location;
import android.provider.BaseColumns;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.InputType;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.SimpleCursorAdapter;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.GoogleApiAvailability;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;


public class MainActivity extends AppCompatActivity implements
        GoogleApiClient.ConnectionCallbacks, GoogleApiClient.OnConnectionFailedListener {

    private GoogleApiClient mGoogleApiClient;
    private LocationRequest mLocationRequest;
    private LocationListener mLocationListener;
    private static final int PERMS_REQUEST_CODE = 17;
    String latitude;
    String longitude;
    String userInput;
    SQLiteExample mSQLiteExample;
    Cursor mSQLCursor;
    SimpleCursorAdapter mSQLCursorAdapter;
    private static final String TAG = "SQLActivity";
    SQLiteDatabase mSQLDB;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        if (mGoogleApiClient == null){
            mGoogleApiClient = new GoogleApiClient.Builder(this)
                    .addConnectionCallbacks(this)
                    .addOnConnectionFailedListener(this)
                    .addApi(LocationServices.API)
                    .build();
        }
        mLocationRequest = LocationRequest.create();
        mLocationRequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);
        mLocationRequest.setInterval(500);
        mLocationRequest.setFastestInterval(500);
        mLocationListener = (location) -> {
            if(location != null){
                longitude = String.valueOf(location.getLongitude());
                latitude = String.valueOf(location.getLatitude());
            }
            else{
                latitude = "44.5";
                longitude = "-123.2";
            }
        };

        mSQLiteExample = new SQLiteExample(this);
        mSQLDB = mSQLiteExample.getWritableDatabase();

        Button click = findViewById(R.id.click);
        click.setOnClickListener(view -> {
            EditText input = findViewById(R.id.input);
            input.setInputType(InputType.TYPE_CLASS_TEXT);
            userInput = input.getText().toString();
            updateLocation();
            if (mSQLDB != null) {
                ContentValues vals = new ContentValues();
                vals.put(DBContract.DemoTable.COLUMN_NAME_DEMO_STRING, ((EditText) findViewById(R.id.input)).getText().toString());
                vals.put(DBContract.DemoTable.COLUMN_NAME_DEMO_LATITUDE, latitude);
                vals.put(DBContract.DemoTable.COLUMN_NAME_DEMO_LONGITUDE, longitude);
                mSQLDB.insert(DBContract.DemoTable.TABLE_NAME, null, vals);
            }
            else{
                Log.d(TAG, "Unable to write to database");
            }
        });
        Button data = findViewById(R.id.data);
        data.setOnClickListener(view -> populateTable());
    }
    @Override
    protected void onStart() {
        mGoogleApiClient.connect();
        super.onStart();
    }

    @Override
    protected void onStop(){
        mGoogleApiClient.disconnect();
        super.onStop();
    }

    private void updateLocation(){
        if (ActivityCompat.checkSelfPermission(this,
                Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
                ActivityCompat.checkSelfPermission(this,
                        Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            latitude = "44.5";
            longitude = "-123.2";
            return;
        }
        Location mLastLocation = LocationServices.FusedLocationApi.getLastLocation(mGoogleApiClient);

        if(mLastLocation != null){
            longitude = String.valueOf(mLastLocation.getLongitude());
            latitude = String.valueOf(mLastLocation.getLatitude());
        }
        else{
            LocationServices.FusedLocationApi.requestLocationUpdates(mGoogleApiClient, mLocationRequest, mLocationListener);
        }
    }

    @Override
    public void onConnected(@Nullable Bundle bundle){
        requestPerms();
    }

    @Override
    public void onConnectionSuspended(int i){

    }

    @Override
    public void onConnectionFailed(@NonNull ConnectionResult connectionResult){
        Dialog errDialog = GoogleApiAvailability.getInstance().getErrorDialog(this,
                connectionResult.getErrorCode(),0);
        errDialog.show();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults){
        if(requestCode == PERMS_REQUEST_CODE){
            if(grantResults.length > 0){
                updateLocation();
            }
        }
    }

    private void requestPerms() {
        if (ActivityCompat.checkSelfPermission(this,
                Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
                ActivityCompat.checkSelfPermission(this,
                        Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, PERMS_REQUEST_CODE);
        }
    }

    private void populateTable(){
        if(mSQLDB != null) try {
            if (mSQLCursorAdapter != null && mSQLCursorAdapter.getCursor() != null) {
                if (!mSQLCursorAdapter.getCursor().isClosed()) {
                    mSQLCursorAdapter.getCursor().close();
                }
            }
            mSQLCursor = mSQLDB.query(DBContract.DemoTable.TABLE_NAME,
                    new String[]{DBContract.DemoTable._ID,
                            DBContract.DemoTable.COLUMN_NAME_DEMO_STRING,
                            DBContract.DemoTable.COLUMN_NAME_DEMO_LATITUDE,
                            DBContract.DemoTable.COLUMN_NAME_DEMO_LONGITUDE},
                    null, null, null, null, null);
            ListView SQListView = findViewById(R.id.list_view);
            mSQLCursorAdapter = new SimpleCursorAdapter(this,
                    R.layout.sql_item,
                    mSQLCursor,
                    new String[]{DBContract.DemoTable.COLUMN_NAME_DEMO_STRING,
                            DBContract.DemoTable.COLUMN_NAME_DEMO_LATITUDE,
                            DBContract.DemoTable.COLUMN_NAME_DEMO_LONGITUDE},
                    new int[]{R.id.sql_listview_string, R.id.sql_listview_lat, R.id.sql_listview_lon}, 0);
            SQListView.setAdapter(mSQLCursorAdapter);
        } catch (Exception e) {
            Log.d(TAG, "Error loading database");
        }

    }

    class SQLiteExample extends SQLiteOpenHelper {
        SQLiteExample(Context context) {
            super(context, DBContract.DemoTable.DB_NAME, null, DBContract.DemoTable.DB_VERSION);
        }

        @Override
        public void onCreate(SQLiteDatabase db){
            db.execSQL(DBContract.DemoTable.SQL_CREATE_DEMO_TABLE);
        }

        @Override
        public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion){
            db.execSQL(DBContract.DemoTable.SQL_DROP_DEMO_TABLE);
            onCreate(db);
        }
    }

    final class DBContract {
        private DBContract(){}

        final class DemoTable implements BaseColumns{
            static final String DB_NAME = "demo_db";
            static final String TABLE_NAME = "demo";
            static final String COLUMN_NAME_DEMO_STRING = "demo_string";
            static final String COLUMN_NAME_DEMO_LATITUDE = "demo_latitude";
            static final String COLUMN_NAME_DEMO_LONGITUDE = "demo_longitude";
            static final int DB_VERSION = 4;

            static final String SQL_CREATE_DEMO_TABLE = "CREATE TABLE " +
                    DemoTable.TABLE_NAME + "(" + DemoTable._ID + " INTEGER PRIMARY KEY NOT NULL," +
                    DemoTable.COLUMN_NAME_DEMO_STRING + " VARCHAR(255)," +
                    DemoTable.COLUMN_NAME_DEMO_LATITUDE + " VARCHAR(255)," +
                    DemoTable.COLUMN_NAME_DEMO_LONGITUDE + " VARCHAR(255));";
            static final String SQL_DROP_DEMO_TABLE = "DROP TABLE IF EXISTS " + DemoTable.TABLE_NAME;
        }
    }
}