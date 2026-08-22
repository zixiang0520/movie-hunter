"""Service layer — combines TMDB calls into rich detail objects."""
from __future__ import annotations

from typing import Any

from .models import (
    AppSettings,
    CastMember,
    CrewMember,
    Genre,
    MovieDetail,
    PersonDetails,
    ProductionCompany,
    ProductionCountry,
    SeasonDetail,
    TVDetail,
)
from .tmdb_client import TMDBClient


def _first_genre(g: dict) -> Genre:
    return Genre(id=g.get("id", 0), name=g.get("name", ""))


def _first_cast(c: dict) -> CastMember:
    return CastMember(
        id=c.get("id", 0),
        name=c.get("name", ""),
        character=c.get("character", ""),
        profile_path=c.get("profile_path"),
        order=c.get("order", 0),
    )


def _first_crew(c: dict) -> CrewMember:
    return CrewMember(
        id=c.get("id", 0),
        name=c.get("name", ""),
        job=c.get("job", ""),
        department=c.get("department", ""),
        profile_path=c.get("profile_path"),
    )


def fetch_movie_detail(client: TMDBClient, movie_id: int) -> MovieDetail:
    data = client.get_movie(movie_id)
    credits = client.get_movie_credits(movie_id)
    similar = client.get_movie_similar(movie_id)

    detail = MovieDetail(
        id=data.get("id", 0),
        title=data.get("title", ""),
        overview=data.get("overview", ""),
        poster_path=data.get("poster_path"),
        backdrop_path=data.get("backdrop_path"),
        release_date=data.get("release_date", ""),
        runtime=data.get("runtime", 0),
        vote_average=data.get("vote_average", 0.0),
        vote_count=data.get("vote_count", 0),
        popularity=data.get("popularity", 0.0),
        tagline=data.get("tagline", ""),
        genres=[_first_genre(g) for g in data.get("genres", [])],
        production_companies=[
            ProductionCompany(**g)
            for g in data.get("production_companies", [])
        ],
        original_language=data.get("original_language", ""),
        original_title=data.get("original_title", ""),
        status=data.get("status", ""),
        budget=data.get("budget", 0),
        revenue=data.get("revenue", 0),
        cast=[_first_cast(c) for c in credits.get("cast", [])],
        crew=[_first_crew(c) for c in credits.get("crew", [])],
        similar=similar.get("results", []),
    )
    return detail


def fetch_tv_detail(client: TMDBClient, tv_id: int) -> TVDetail:
    data = client.get_tv(tv_id)
    credits = client.get_tv_credits(tv_id)
    similar = client.get_tv_similar(tv_id)

    detail = TVDetail(
        id=data.get("id", 0),
        name=data.get("name", ""),
        overview=data.get("overview", ""),
        poster_path=data.get("poster_path"),
        backdrop_path=data.get("backdrop_path"),
        first_air_date=data.get("first_air_date", ""),
        vote_average=data.get("vote_average", 0.0),
        vote_count=data.get("vote_count", 0),
        popularity=data.get("popularity", 0.0),
        genres=[_first_genre(g) for g in data.get("genres", [])],
        production_companies=[
            ProductionCompany(**c) for c in data.get("production_companies", [])
        ],
        original_language=data.get("original_language", ""),
        original_name=data.get("original_name", ""),
        status=data.get("status", ""),
        episode_run_time=data.get("episode_run_time", []),
        number_of_seasons=data.get("number_of_seasons", 0),
        number_of_episodes=data.get("number_of_episodes", 0),
        seasons=data.get("seasons", []),
        cast=[_first_cast(c) for c in credits.get("cast", [])],
        crew=[_first_crew(c) for c in credits.get("crew", [])],
        similar=similar.get("results", []),
    )
    return detail


def fetch_person_detail(client: TMDBClient, person_id: int) -> PersonDetails:
    data = client.get_person(person_id)
    return PersonDetails(
        id=data.get("id", 0),
        name=data.get("name", ""),
        biography=data.get("biography", ""),
        profile_path=data.get("profile_path"),
        birthday=data.get("birthday"),
        known_for_department=data.get("known_for_department", ""),
        also_known_as=data.get("also_known_as", []),
        popularity=data.get("popularity", 0.0),
        gender=data.get("gender", 0),
        deathday=data.get("deathday"),
        place_of_birth=data.get("place_of_birth"),
    )
