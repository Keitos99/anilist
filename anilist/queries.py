SEARCH_ANIME = """
query ($page: Int, $perPage: Int, $search: String, $id: Int) {
    Page(page: $page, perPage: $perPage) {
      pageInfo {
        total
        perPage
      }
      media(search: $search, id: $id,type: ANIME, sort: FAVOURITES_DESC) {
        id
        synonyms
        type
        title {
            romaji
            english
            native
            userPreferred
        }
        startDate {
            year
            month
            day
        }
        endDate {
            year
            month
            day
        }
        coverImage {
            large
        }
        tags {
            name
        }
        isAdult
        bannerImage
        format
        episodes
        status
        description
        averageScore
        meanScore
        genres
        synonyms
      }
    }
  }
"""

SEARCH_MANGA = """
query ($page: Int, $perPage: Int, $search: String, $id: Int) {
    Page(page: $page, perPage: $perPage) {
      pageInfo {
        total
        perPage
      }
      media(search: $search, id: $id,type: MANGA, sort: FAVOURITES_DESC) {
        id
        synonyms
        type
        title {
            romaji
            english
            native
            userPreferred
        }
        startDate {
            year
            month
            day
        }
        endDate {
            year
            month
            day
        }
        coverImage {
            large
        }
        tags {
            name
        }
        isAdult
        bannerImage
        format
        chapters
        volumes
        status
        description
        averageScore
        meanScore
        genres
        synonyms
      }
    }
  }
"""


MANGA_LIST_COLLECTION_QUERY = """
query MangaListCollectionQuery(
    $userId: Int
) {
    MediaListCollection(
        userId: $userId,
        type: MANGA
    ) {
        lists {
            name
            isCustomList
            isSplitCompletedList
            status
            entries {
                id
                status
                score
                progress
                progressVolumes
                repeat
                priority
                private
                notes
                hiddenFromStatusLists
                customLists
                advancedScores
                startedAt {
                    year
                    month
                    day
                }
                completedAt {
                    year
                    month
                    day
                }
                updatedAt
                createdAt
                media {
                    id
                    synonyms
                    type
                    title {
                        romaji
                        english
                        native
                        userPreferred
                    }
                    startDate {
                        year
                        month
                        day
                    }
                    endDate {
                        year
                        month
                        day
                    }
                    coverImage {
                        large
                    }
                    tags {
                        name
                    }
                    isAdult
                    bannerImage
                    format
                    chapters
                    volumes
                    status
                    description
                    averageScore
                    meanScore
                    genres
                    synonyms
                }
            }
        }
    }
}
"""

SEARCH_USER_QUERY = """
query SearchUsersQuery(
    $page: Int,
    $search: String,
    $sort: [UserSort]
) {
    Page(page: $page) {
        pageInfo {
            total
            perPage
            currentPage
            lastPage
            hasNextPage
        }
        users(search: $search, sort: $sort) {
            id
            name
            avatar {
                large
            }
            siteUrl
            previousNames {
                name
                createdAt
                updatedAt
            }
            statistics {
                anime {
                    count
                }
                manga {
                    count
                }

            }
        }
    }
}
"""

MEDIA_PROGRESS_MUTATION = """
    mutation ($mediaId: Int, $status: MediaListStatus, $progress: Int) {
        SaveMediaListEntry (mediaId: $mediaId, status: $status, progress: $progress ) {
            id
            mediaId
            status
            progress
        }
    }
"""

GET_USERNAME_QUERY = """
query {
    Viewer {
        name
    }
}
"""
