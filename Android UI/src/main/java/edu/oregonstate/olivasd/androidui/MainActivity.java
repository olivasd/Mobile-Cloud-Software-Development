package edu.oregonstate.olivasd.androidui;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button act1btn = findViewById(R.id.act1btn);
        act1btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent startIntent = new Intent(getApplicationContext(), Activity1.class);
                startActivity(startIntent);
            }
        });
        Button act2btn = findViewById(R.id.act2btn);
        act2btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent startIntent = new Intent(getApplicationContext(), Activity2.class);
                startActivity(startIntent);
            }
        });
        Button act3btn = findViewById(R.id.act3btn);
        act3btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent startIntent = new Intent(getApplicationContext(), Activity3.class);
                startActivity(startIntent);
            }
        });
        Button act4btn = findViewById(R.id.act4btn);
        act4btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent startIntent = new Intent(getApplicationContext(), Activity4.class);
                startActivity(startIntent);
            }
        });
    }
}
