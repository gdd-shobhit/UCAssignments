
% -----------------------------------------------------------------------------
% 1. BASIC RELATIONSHIPS FOR REFERENCE
% -----------------------------------------------------------------------------
% parent(X, Y) means X is a parent of Y.
% male(X) / female(X) is gender.

% Parent Relationships---------------------------------------------------------
parent(raj, anjali).
parent(raj, arjun).
parent(priya, anjali).
parent(priya, arjun).
parent(anjali, meera).
parent(anjali, vikram).
parent(arjun, rohan).
parent(arjun, kavya).
parent(meera, diya).
parent(meera, dev).

% Gender Relationships---------------------------------------------------------
male(raj).
male(arjun).
male(vikram).
male(rohan).
male(dev).
female(priya).
female(anjali).
female(meera).
female(kavya).
female(diya).

% -----------------------------------------------------------------------------
% 2. DERIVED RELATIONSHIPS (Rules)
% -----------------------------------------------------------------------------

% Grandparent: X is a grandparent of Y if X is a parent of some Z who is a, kinda confusing but yeah
% parent of Y. (Uses the parent relation; recursive descendant below.)
grandparent(X, Y) :-
    parent(X, Z),
    parent(Z, Y).

% Sibling: X and Y are siblings if they share the same parent (and are distinct).
sibling(X, Y) :-
    parent(P, X),
    parent(P, Y),
    X \= Y.

% Cousin: X and Y are cousins if they have parents who are siblings (and X, Y distinct).
cousin(X, Y) :-
    parent(PX, X),
    parent(PY, Y),
    sibling(PX, PY),
    X \= Y.

% Helper: child(X, Y) means X is a child of Y (inverse of parent for querying).
child(X, Y) :-
    parent(Y, X).

% -----------------------------------------------------------------------------
% 3. RECURSIVE LOGIC — Indirect relationships
% -----------------------------------------------------------------------------
% Descendant: X is a descendant of Y if Y is an ancestor of X.
% Base case: X is a direct child of Y.
% Recursive case: X is a descendant of some child Z of Y.

descendant(X, Y) :-
    parent(Y, X).
descendant(X, Y) :-
    parent(Y, Z),
    descendant(X, Z).

% Ancestor: X is an ancestor of Y iff Y is a descendant of X.
ancestor(X, Y) :-
    descendant(Y, X).

% -----------------------------------------------------------------------------
% EXAMPLE QUERIES
% -----------------------------------------------------------------------------
% Run in a Prolog interpreter (e.g., SWI-Prolog): consult('family_tree.pl').
%
% Who are the children of a particular person?
%   ?- child(C, raj).         % C = anjali ; C = arjun.
%   ?- child(C, anjali).      % C = meera ; C = vikram.
%
% Who are the siblings of a particular person?
%   ?- sibling(anjali, S).    % S = arjun.
%   ?- sibling(meera, S).     % S = vikram.
%
% Is one person a cousin of another?
%   ?- cousin(meera, rohan).  % true (anjali and arjun are siblings).
%   ?- cousin(X, rohan).      % X = meera ; X = vikram.
%
% Who are the grandparents of a person?
%   ?- grandparent(G, meera). % G = raj ; G = priya.
%
% All descendants of a person (recursive):
%   ?- descendant(D, raj).    % D = anjali ; D = arjun ; D = meera ; D = vikram ; ...
%   ?- descendant(D, anjali). % D = meera ; D = vikram ; D = diya ; D = dev.
%
% All ancestors of a person:
%   ?- ancestor(A, diya).     % A = meera ; A = anjali ; A = raj ; A = priya.
% =============================================================================
