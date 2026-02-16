package com.metablooms.quickupload.data.github

import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object GitHubClient {

    private const val API_BASE = "https://api.github.com/"
    private const val AUTH_BASE = "https://github.com/"

    fun createApi(tokenProvider: () -> String?): GitHubApi {
        val client = buildOkHttpClient(tokenProvider)
        return Retrofit.Builder()
            .baseUrl(API_BASE)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(GitHubApi::class.java)
    }

    fun createAuthApi(): GitHubAuthApi {
        val client = OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
        return Retrofit.Builder()
            .baseUrl(AUTH_BASE)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(GitHubAuthApi::class.java)
    }

    private fun buildOkHttpClient(tokenProvider: () -> String?): OkHttpClient {
        val authInterceptor = Interceptor { chain ->
            val request = chain.request().newBuilder().apply {
                tokenProvider()?.let { token ->
                    addHeader("Authorization", "Bearer $token")
                }
                addHeader("Accept", "application/vnd.github.v3+json")
                addHeader("X-GitHub-Api-Version", "2022-11-28")
            }.build()
            chain.proceed(request)
        }

        // Logging interceptor that redacts Authorization header
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
            redactHeader("Authorization")
        }

        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build()
    }
}
