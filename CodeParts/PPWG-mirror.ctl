; Periodically patterned waveguide.

(set! default-material air)

; Polarization to use
(define-param pol TM)

; Structure geometry
(define-param nrod 2.4)	; Rod refractive index
(define-param rrod 0.3)	; Starting filling fraction in units of the lattice constant
(define-param rend 0.1) ; Ending filling fraction in units of the lattice constant
(define-param wbm 1.0)	; Beam width in units of the lattice constant
(define-param lbm 40.0) ; Bean length in units of the lattice constant
(define-param mir 15.0) ; Number of mirror segments in units of the lattice constant
(define-param nbm 1.0)	; Beam refractive index
(define-param shift 0.5)	; Hole shift in the unit cell

; Simulation parameters
(define-param nbands 3)	; Number of bands to compute
(define-param nks 16)	; Number of k-points to compute
(define-param res 64)	; Resolution
(define-param doplot 1)	; Should we plot fields?

(define filename-prefix (string-append "r" (number->string rrod) "-"))

; Define the materials (for a cleaner geometry declaration afterwards)
(define rod-material
    (make dielectric (index nrod))
)
(define bm-material
    (make dielectric (index nbm))
)

(set! num-bands nbands)
(set! k-points (list 
;		    (vector3 -0.5 0 0)
		    (vector3 0 0 0)
		    (vector3 0.5 0 0)
		)
)

(set! k-points (interpolate nks k-points))

(set! geometry-lattice 
    (make lattice (size 50 3 no-size))
)

; Set taper profile (quadratic)
(define (quad s e m)
	(/ (- s e) (expt (- m 1) 2) )
)
	


; Rod geometry
(define (mirholes m mmax dm s)
	(if (<= m mmax)
	    (begin
	       (set! geometry 
		  (append geometry
	        (list 
			(make cylinder
           		(center (+ shift m) 0 0)
           		(radius (- s ( * (quad rrod rend mir) (expt m 2))))
           		(height infinity)
         		(material rod-material)
	    		)
	    	(make cylinder
				(center (- (- 0 shift) m) 0 0)
				(radius (- s ( * (quad rrod rend mir) (expt m 2))))
				(height infinity)
				(material rod-material)
	    		)
	            )
	          )
		)
	    	(mirholes (+ m dm) mmax dm s)
	    )
    )
)

(define (addholes n nmax dn e)
	(if (<= n nmax)
	    (begin
	       (set! geometry 
	          (append geometry
		      (list
			(make cylinder
				(center (+ shift n) 0 0)
				(radius e)
				(height infinity)
				(material rod-material)
			)
			(make cylinder
				(center (- (- 0 shift) n) 0 0)
				(radius e)
				(height infinity)
				(material rod-material)
			)
		      )
		   )
		)
		(addholes (+ n dn) nmax dn e)
	    )
	)
)
; Block geometry
(define (block-geom l w)
	(set! geometry
		(list
			(make block
				(center 0 0 0)
				(size l w infinity)
				(material bm-material)
			)
		)
	)
)

; Define the geometry

(block-geom lbm wbm)
(mirholes 0 15 1 rrod)
(addholes mir (- (/ lbm 2) 1) 1 rend) 



(set! resolution res)
(set! mesh-size 7)

(cond
    ((= pol TM)
	(if (zero? doplot)
	    (run-tm)
	    (run-tm
		(output-at-kpoint (vector3 0.5 0 0) output-efield-z)
		(output-at-kpoint (vector3 0.5 0 0) output-hfield)
		(output-at-kpoint (vector3 0.5 0 0) output-dpwr)
	    )
	)
    )
    ((= pol TE)
	(if (zero? doplot)
	    (run-te)
	    (run-te-yodd
		(output-at-kpoint (vector3 0.5 0 0) output-hfield-z)
		(output-at-kpoint (vector3 0.5 0 0) output-efield)
		(output-at-kpoint (vector3 0.5 0 0) output-dpwr)
	    )
	)
    )
    (else (display "Ill-defined polarization!\n"))
)
