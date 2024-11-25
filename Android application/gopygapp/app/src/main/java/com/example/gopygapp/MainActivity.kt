package com.example.gopygapp

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.*
import android.widget.Button
import com.example.gopygapp.R

class MainActivity : Activity() {

    // Initializing webview, upload confirmation link and file chooser
    private lateinit var webView: WebView
    private var mUploadMessage: ValueCallback<Array<Uri>>? = null   // Callback for file upload
    private val FILECHOOSER_RESULTCODE = 1  // Result code for file chooser interface

    // Creating the actual app Launch instance
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)  // Call to the superclass method
        setContentView(R.layout.activity_main)  // Set the layout for the activity

        // Setting up webView with pinch to zoom and other settings
        webView = findViewById(R.id.webview)    // Find the webview in the layout
        val webSettings: WebSettings = webView.settings // Get the web settings for the webview
        webSettings.javaScriptEnabled = true    // Enable JS to modify screen size
        webSettings.domStorageEnabled = true    // Enable DOM storage
        webSettings.useWideViewPort = true // Enable Wide viewport
        webSettings.loadWithOverviewMode = true // Fits content to screen width initially (override to make screen big enough)
        webSettings.builtInZoomControls = true // Pinchto-zoom controls enabled
        webSettings.displayZoomControls = false // Hide default zoom controls
        webSettings.setSupportZoom(true) // Enable pinch-to-zoom functionality

        // Injecting JavaScript to modify the page layout after it has finished loading
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                // JavaScript to add a meta tag for zooming and scaling
                view?.evaluateJavascript(
                    """
                    (function() {
                        var meta = document.querySelector('meta[name="viewport"]');
                        if (!meta) {
                            meta = document.createElement('meta');
                            meta.name = 'viewport';
                            document.head.appendChild(meta);
                        }
                        // Set to initial scale and allow user scaling 
                        meta.content = 'width='+(window.innerWidth*1.15)+', initial-scale=1.0, user-scalable=yes';
                    })();
                    """.trimIndent(),
                    null
                )
            }
        }

        // Loading Streamlit app url into webview
        if (savedInstanceState == null) {
            webView.loadUrl("https://pygotesting.streamlit.app/")
        }

        // Set up file chooser for uploads
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                // Clear previous upload message if it exists
                if (mUploadMessage != null) {
                    mUploadMessage?.onReceiveValue(null)
                }
                mUploadMessage = filePathCallback   // Set the new file path callback

                // Create an intent to open the file chooser
                val intent = Intent(Intent.ACTION_GET_CONTENT)
                intent.addCategory(Intent.CATEGORY_OPENABLE)    // Allow opening files
                intent.type = "*/*" / Allow all file types
                val mimeTypes = arrayOf(
                    "text/csv",     // Allow CSV files
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" // Allow XLSX files
                )
                intent.putExtra(Intent.EXTRA_MIME_TYPES, mimeTypes) // Set allowed MIME types
                // Ensuring that file selected is legit
                try {
                    startActivityForResult(
                        Intent.createChooser(intent, "Select a File"),  // Show file chooser   
                        FILECHOOSER_RESULTCODE  // Use predefined result code
                    )
                } catch (e: Exception) {
                    mUploadMessage = null   // Reset upload message on error
                    return false    // Return false if there was an error
                }
                return true     // Return true to indicate the file chooser was shown
            }
        }

        // Rotate screen button (labeled as rotate/restart)
        val btnToggleOrientation: Button = findViewById(R.id.btn_landscape) // Find the button in the layout
        btnToggleOrientation.setOnClickListener {
            // Toggle between portrait and landscape orientations
            if (resources.configuration.orientation == android.content.res.Configuration.ORIENTATION_PORTRAIT) {
                // Set to landscape
                requestedOrientation = android.content.pm.ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
            } else {
                // Set to portrait
                requestedOrientation = android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
            }
        }
    }
    //attempting to save instance state (not really functional as is)
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState) // Save the state of the webview
    }
    //continuation of above function purpose
    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        webView.restoreState(savedInstanceState)    // Restore the state of the webview
    }
    // Interface for filechooser and fastAPI
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == FILECHOOSER_RESULTCODE) {    // Check if the result is from the file chooser
            if (mUploadMessage == null) return      // Return if there is no upload message
            val result = data?.data         // Get the result data
            mUploadMessage?.onReceiveValue(arrayOf(result ?: Uri.EMPTY))    // Send the result back to the callback
            mUploadMessage = null       // Reset the upload message
        }
        super.onActivityResult(requestCode, resultCode, data)
    }
}
