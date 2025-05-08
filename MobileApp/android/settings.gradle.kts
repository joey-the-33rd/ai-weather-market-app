pluginManagement {
    repositories {
        google() // For Android Gradle Plugin and Google dependencies
        mavenCentral() // For Kotlin and other libraries
        gradlePluginPortal() // For Gradle community plugins
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS) // Enforces repo centralization
    repositories {
        google() // For Android and Google dependencies
        mavenCentral() // For Kotlin and other libraries
    }
}
