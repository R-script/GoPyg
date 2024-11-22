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
    private var mUploadMessage: ValueCallback<Array<Uri>>? = null
    private val FILECHOOSER_RESULTCODE = 1  // Used as interface between fastAPI python code and .apk

    // Creating the actual app Launch instance
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Settping up webView with pinch to zoom etc.
        webView = findViewById(R.id.webview)
        val webSettings: WebSettings = webView.settings
        webSettings.javaScriptEnabled = true // Enable JS to modify screen size
        webSettings.domStorageEnabled = true 
        webSettings.useWideViewPort = true // Wide viewport
        webSettings.loadWithOverviewMode = true // Fits content to screen width initially (override to make screen big enough)
        webSettings.builtInZoomControls = true // Pinch to zoom controls enabled
        webSettings.displayZoomControls = false // Hide default zoom controls
        webSettings.setSupportZoom(true) // Enable pinch-to-zoom

        // Injecting JS to modify the page layout
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
                        // Set to initial scale and allow user scaling --not sure why width needs separated from window.innerWidth
                        meta.content = 'width='+(window.innerWidth*1.15)+', initial-scale=1.0, user-scalable=yes';
                    })();
                    """.trimIndent(),
                    null
                )
            }
        }

        // Loading Streamlit app url
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
                if (mUploadMessage != null) {
                    mUploadMessage?.onReceiveValue(null)
                }
                mUploadMessage = filePathCallback

                val intent = Intent(Intent.ACTION_GET_CONTENT)
                intent.addCategory(Intent.CATEGORY_OPENABLE)
                intent.type = "*/*"
                val mimeTypes = arrayOf(
                    "text/csv",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                intent.putExtra(Intent.EXTRA_MIME_TYPES, mimeTypes)
                // Ensuring that file selected is legit
                try {
                    startActivityForResult(
                        Intent.createChooser(intent, "Select a File"),
                        FILECHOOSER_RESULTCODE
                    )
                } catch (e: Exception) {
                    mUploadMessage = null
                    return false
                }
                return true
            }
        }

        // Rotate screen button (labeled as rotate/restart)
        val btnToggleOrientation: Button = findViewById(R.id.btn_landscape)
        btnToggleOrientation.setOnClickListener {
            if (resources.configuration.orientation == android.content.res.Configuration.ORIENTATION_PORTRAIT) {
                requestedOrientation = android.content.pm.ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
            } else {
                requestedOrientation = android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
            }
        }
    }
    //attempting to save instance state (not really functional as is)
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }
    //continuation of above function purpose
    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        webView.restoreState(savedInstanceState)
    }
    // Interface for filechooser and fastAPI
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == FILECHOOSER_RESULTCODE) {
            if (mUploadMessage == null) return
            val result = data?.data
            mUploadMessage?.onReceiveValue(arrayOf(result ?: Uri.EMPTY))
            mUploadMessage = null
        }
        super.onActivityResult(requestCode, resultCode, data)
    }
}
